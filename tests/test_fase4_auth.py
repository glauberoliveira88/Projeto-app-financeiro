"""Testes automatizados da Fase 4 — Autenticação, Sessão, Google OAuth e Proteção de Rotas.

Valida os fluxos de:
1. Cadastro com provisionamento canônico (10 categorias e carteira padrão inicial);
2. Validações de cadastro (senha curta, e-mail duplicado, confirmação divergente);
3. Login tradicional, sessão persistente e logout;
4. Proteção contra força bruta (5 tentativas falhas -> bloqueio 15 min / HTTP 429);
5. Recuperação de senha, mitigação de enumeração e redefinição com token;
6. Decorador @login_required e proteção contra IDOR (validar_posse);
7. Fluxo Google OAuth 2.0 com provisionamento automático e tratamento de erros.
"""
import unittest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from flask import session
from app import create_app
from app.models import (
    db,
    Usuario,
    Conta,
    Categoria,
    LogSeguranca,
)
from app.utils.auth import login_required, validar_posse


class TestFase4Autenticacao(unittest.TestCase):
    """Suíte de testes para a Fase 4."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def setUp(self):
        """Prepara o cliente de teste e limpa dados de execuções anteriores."""
        self.client = self.app.test_client()
        self.limpar_dados_teste()

    def tearDown(self):
        """Limpa dados após cada teste."""
        db.session.remove()
        self.limpar_dados_teste()

    def limpar_dados_teste(self):
        """Remove registros com e-mails de teste."""
        try:
            usuarios = Usuario.query.filter(Usuario.email.like("%@teste.com")).all()
            for u in usuarios:
                LogSeguranca.query.filter_by(usuario_id=u.id).delete()
                Conta.query.filter_by(usuario_id=u.id).delete()
                Categoria.query.filter_by(usuario_id=u.id).delete()
                db.session.delete(u)
            
            # Limpa logs de segurança soltos de teste
            LogSeguranca.query.filter(
                db.or_(
                    LogSeguranca.detalhes.like("%@teste.com%"),
                    LogSeguranca.ip == "192.168.10.50",
                )
            ).delete()
            db.session.commit()
        except Exception:
            db.session.rollback()

    def test_01_cadastro_sucesso_com_provisionamento(self):
        """Testa o cadastro bem-sucedido e o provisionamento automático das 10 categorias e da carteira padrão."""
        payload = {
            "nome": "Arthur Silva",
            "email": "arthur@teste.com",
            "senha": "SenhaForte123",
            "confirmacao_senha": "SenhaForte123",
        }
        res = self.client.post("/api/auth/cadastro", json=payload)
        self.assertEqual(res.status_code, 201)
        dados = res.get_json()
        self.assertTrue(dados["sucesso"])
        self.assertEqual(dados["dados"]["usuario"]["email"], "arthur@teste.com")

        # Verifica se o usuário foi persistido no banco
        usuario = Usuario.query.filter_by(email="arthur@teste.com").first()
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.nome, "Arthur Silva")
        self.assertTrue(usuario.verificar_senha("SenhaForte123"))

        # Verifica o provisionamento da carteira inicial padrão "Carteira"
        contas = Conta.query.filter_by(usuario_id=usuario.id).all()
        self.assertEqual(len(contas), 1)
        self.assertEqual(contas[0].nome, "Carteira")
        self.assertEqual(contas[0].saldo_inicial, Decimal("0.00"))
        self.assertEqual(contas[0].status, "ativo")

        # Verifica o provisionamento da lista canônica das 10 categorias padrão (FSD 6.6)
        categorias = Categoria.query.filter_by(usuario_id=usuario.id).all()
        self.assertEqual(len(categorias), 10)

        cats_receita = [c.nome for c in categorias if c.tipo == "receita"]
        cats_despesa = [c.nome for c in categorias if c.tipo == "despesa"]

        self.assertEqual(len(cats_receita), 3)
        self.assertIn("Salário", cats_receita)
        self.assertIn("Rendimentos", cats_receita)
        self.assertIn("Outras Receitas", cats_receita)

        self.assertEqual(len(cats_despesa), 7)
        self.assertIn("Alimentação", cats_despesa)
        self.assertIn("Moradia", cats_despesa)
        self.assertIn("Transporte", cats_despesa)
        self.assertIn("Saúde", cats_despesa)
        self.assertIn("Educação", cats_despesa)
        self.assertIn("Lazer", cats_despesa)
        self.assertIn("Outras Despesas", cats_despesa)

        # Verifica registro de evento de segurança
        log = LogSeguranca.query.filter_by(usuario_id=usuario.id, evento="CADASTRO_SUCESSO").first()
        self.assertIsNotNone(log)

    def test_02_cadastro_validacoes(self):
        """Validações de campos no cadastro (senha curta, e-mail inválido, duplicidade)."""
        # Senha com menos de 8 caracteres
        res = self.client.post("/api/auth/cadastro", json={
            "nome": "Teste",
            "email": "curta@teste.com",
            "senha": "1234567",
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("mínimo 8 caracteres", res.get_json()["erro"])

        # Confirmação divergente
        res = self.client.post("/api/auth/cadastro", json={
            "nome": "Teste",
            "email": "div@teste.com",
            "senha": "SenhaForte123",
            "confirmacao_senha": "OutraSenha123",
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("confirmação de senha", res.get_json()["erro"])

        # E-mail inválido
        res = self.client.post("/api/auth/cadastro", json={
            "nome": "Teste",
            "email": "email_invalido_sem_arroba",
            "senha": "SenhaForte123",
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("e-mail válido", res.get_json()["erro"])

        # E-mail já cadastrado
        self.client.post("/api/auth/cadastro", json={
            "nome": "Primeiro",
            "email": "duplicado@teste.com",
            "senha": "SenhaForte123",
        })
        res_dup = self.client.post("/api/auth/cadastro", json={
            "nome": "Segundo",
            "email": "duplicado@teste.com",
            "senha": "SenhaForte123",
        })
        self.assertEqual(res_dup.status_code, 400)
        self.assertIn("já está cadastrado", res_dup.get_json()["erro"])

    def test_03_login_sucesso_sessao_e_logout(self):
        """Testa o ciclo completo de login tradicional, consulta de sessão e logout."""
        # Cadastra o usuário
        self.client.post("/api/auth/cadastro", json={
            "nome": "Beatriz Santos",
            "email": "beatriz@teste.com",
            "senha": "SenhaForte123",
        })

        # Desloga para testar login explicitamente
        self.client.post("/api/auth/logout")

        # Verifica sessão deslogada
        res_sessao1 = self.client.get("/api/auth/sessao")
        self.assertEqual(res_sessao1.status_code, 200)
        self.assertFalse(res_sessao1.get_json()["autenticado"])

        # Efetua login
        res_login = self.client.post("/api/auth/login", json={
            "email": "beatriz@teste.com",
            "senha": "SenhaForte123",
        })
        self.assertEqual(res_login.status_code, 200)
        self.assertTrue(res_login.get_json()["sucesso"])
        self.assertEqual(res_login.get_json()["dados"]["usuario"]["email"], "beatriz@teste.com")

        # Consulta sessão autenticada
        res_sessao2 = self.client.get("/api/auth/sessao")
        self.assertEqual(res_sessao2.status_code, 200)
        dados_sessao = res_sessao2.get_json()
        self.assertTrue(dados_sessao["autenticado"])
        self.assertEqual(dados_sessao["dados"]["usuario"]["email"], "beatriz@teste.com")

        # Efetua logout
        res_logout = self.client.post("/api/auth/logout")
        self.assertEqual(res_logout.status_code, 200)
        self.assertTrue(res_logout.get_json()["sucesso"])

        # Confirma que a sessão foi destruída
        res_sessao3 = self.client.get("/api/auth/sessao")
        self.assertFalse(res_sessao3.get_json()["autenticado"])

    def test_04_login_credenciais_invalidas_e_defesa_forca_bruta(self):
        """Testa erro de credenciais e o bloqueio de força bruta após 5 falhas consecutivas (FSD Seção 6 e 15)."""
        email_teste = "bruteforce@teste.com"
        ip_teste = "192.168.10.50"

        # Cadastra o usuário para testar falhas de senha
        self.client.post("/api/auth/cadastro", json={
            "nome": "Usuário Alvo",
            "email": email_teste,
            "senha": "SenhaCorreta123",
        })
        self.client.post("/api/auth/logout")

        # Realiza 4 tentativas com senha incorreta
        for i in range(4):
            res = self.client.post(
                "/api/auth/login",
                json={"email": email_teste, "senha": f"SenhaIncorreta_{i}"},
                environ_base={"REMOTE_ADDR": ip_teste},
            )
            self.assertEqual(res.status_code, 401)
            self.assertIn("E-mail ou senha incorretos", res.get_json()["erro"])

        # 5ª tentativa falha (deve retornar 401 e contabilizar a 5ª tentativa)
        res_5 = self.client.post(
            "/api/auth/login",
            json={"email": email_teste, "senha": "SenhaIncorreta_5"},
            environ_base={"REMOTE_ADDR": ip_teste},
        )
        self.assertEqual(res_5.status_code, 401)

        # 6ª tentativa: agora o IP/e-mail deve estar bloqueado por força bruta (HTTP 429)
        res_bloqueado = self.client.post(
            "/api/auth/login",
            json={"email": email_teste, "senha": "SenhaCorreta123"},
            environ_base={"REMOTE_ADDR": ip_teste},
        )
        self.assertEqual(res_bloqueado.status_code, 429)
        dados_bloqueio = res_bloqueado.get_json()
        self.assertFalse(dados_bloqueio["sucesso"])
        self.assertIn("bloqueado", dados_bloqueio["erro"])

        # Confirma o registro do bloqueio em logs_seguranca
        log_bloqueio = LogSeguranca.query.filter_by(
            ip=ip_teste, evento="BLOQUEIO_FORCA_BRUTA"
        ).first()
        self.assertIsNotNone(log_bloqueio)

    def test_05_recuperacao_e_redefinicao_senha(self):
        """Testa o fluxo de recuperação de senha, mitigação de enumeração e redefinição com token temporário."""
        email_user = "recuperar@teste.com"
        self.client.post("/api/auth/cadastro", json={
            "nome": "Clara Nunes",
            "email": email_user,
            "senha": "SenhaAntiga123",
        })
        self.client.post("/api/auth/logout")

        # 1. Solicitação de recuperação para e-mail existente
        res_rec = self.client.post("/api/auth/recuperar-senha", json={"email": email_user})
        self.assertEqual(res_rec.status_code, 200)
        self.assertTrue(res_rec.get_json()["sucesso"])

        # Verifica token gerado no usuário
        user = Usuario.query.filter_by(email=email_user).first()
        self.assertIsNotNone(user.token_recuperacao)
        token_gerado = user.token_recuperacao

        # 2. Solicitação de recuperação para e-mail inexistente (deve responder a mesma mensagem)
        res_rec_inexistente = self.client.post(
            "/api/auth/recuperar-senha", json={"email": "inexistente@teste.com"}
        )
        self.assertEqual(res_rec_inexistente.status_code, 200)
        self.assertEqual(
            res_rec.get_json()["mensagem"], res_rec_inexistente.get_json()["mensagem"]
        )

        # 3. Tentativa de redefinir senha com token falso
        res_falso = self.client.post("/api/auth/redefinir-senha", json={
            "token": "token_inventado_invalido",
            "nova_senha": "NovaSenhaForte123",
        })
        self.assertEqual(res_falso.status_code, 400)
        self.assertIn("inválido ou expirado", res_falso.get_json()["erro"])

        # 4. Redefinição com senha menor que 8 caracteres
        res_curta = self.client.post("/api/auth/redefinir-senha", json={
            "token": token_gerado,
            "nova_senha": "curta",
        })
        self.assertEqual(res_curta.status_code, 400)
        self.assertIn("mínimo 8 caracteres", res_curta.get_json()["erro"])

        # 5. Redefinição com sucesso
        res_sucesso = self.client.post("/api/auth/redefinir-senha", json={
            "token": token_gerado,
            "nova_senha": "NovaSenhaSuperSegura123",
            "confirmacao_senha": "NovaSenhaSuperSegura123",
        })
        self.assertEqual(res_sucesso.status_code, 200)
        self.assertTrue(res_sucesso.get_json()["sucesso"])

        # Verifica que o token foi invalidado/limpo
        db.session.refresh(user)
        self.assertIsNone(user.token_recuperacao)

        # 6. Login com a nova senha deve funcionar
        res_login_novo = self.client.post("/api/auth/login", json={
            "email": email_user,
            "senha": "NovaSenhaSuperSegura123",
        })
        self.assertEqual(res_login_novo.status_code, 200)

        # Login com a senha antiga deve falhar
        self.client.post("/api/auth/logout")
        res_login_antigo = self.client.post("/api/auth/login", json={
            "email": email_user,
            "senha": "SenhaAntiga123",
        })
        self.assertEqual(res_login_antigo.status_code, 401)

    def test_06_protecao_rotas_login_required_e_idor(self):
        """Testa o decorador @login_required para API/web e a defesa anti-IDOR via validar_posse."""
        # 1. Requisição não autenticada para API deve retornar HTTP 401 Unauthorized
        res_api = self.client.get("/api/auth/protegido-teste")
        self.assertEqual(res_api.status_code, 401)
        self.assertFalse(res_api.get_json()["sucesso"])
        self.assertIn("Autenticação obrigatória", res_api.get_json()["erro"])

        # 2. Requisição não autenticada para rota web protegida deve retornar 302 para /login
        res_web = self.client.get("/dashboard")
        self.assertEqual(res_web.status_code, 302)
        self.assertIn("/login", res_web.headers["Location"])

        # 3. Autentica um usuário e acessa a rota protegida com sucesso
        self.client.post("/api/auth/cadastro", json={
            "nome": "Dono Um",
            "email": "dono1@teste.com",
            "senha": "SenhaForte123",
        })
        res_autenticado = self.client.get("/api/auth/protegido-teste")
        self.assertEqual(res_autenticado.status_code, 200)
        self.assertTrue(res_autenticado.get_json()["sucesso"])

        # 4. Teste da defesa anti-IDOR (validar_posse)
        user1 = Usuario.query.filter_by(email="dono1@teste.com").first()
        user2 = Usuario(nome="Dono Dois", email="dono2@teste.com")
        user2.definir_senha("SenhaForte123")
        db.session.add(user2)
        db.session.commit()

        # Cria uma conta pertencente ao user2
        conta_user2 = Conta(usuario_id=user2.id, nome="Conta Alheia", saldo_inicial=Decimal("100.00"))
        db.session.add(conta_user2)
        db.session.commit()

        # Como a sessão ativa no client é do user1:
        with self.client:
            self.client.get("/api/auth/protegido-teste")
            self.assertFalse(validar_posse(conta_user2, "conta"))

        log_idor = LogSeguranca.query.filter_by(
            usuario_id=user1.id, evento="ACESSO_NEGADO_IDOR"
        ).first()
        self.assertIsNotNone(log_idor)
        self.assertIn("Proprietário=", log_idor.detalhes)

    def test_07_google_oauth_provisionamento_e_callback(self):
        """Testa o provisionamento automático e login via callback simulado do Google OAuth 2.0."""
        # Mock do OAuth2Session para testar o callback com dados simulados do Google
        mock_oauth = MagicMock()
        mock_oauth.fetch_token.return_value = {"access_token": "token_mock_google"}
        
        mock_userinfo_resp = MagicMock()
        mock_userinfo_resp.status_code = 200
        mock_userinfo_resp.json.return_value = {
            "sub": "google_oauth_id_98765",
            "email": "google_usuario@teste.com",
            "name": "Maria Google",
        }
        mock_oauth.get.return_value = mock_userinfo_resp

        with patch("requests_oauthlib.OAuth2Session", return_value=mock_oauth):
            # Simula requisição ao callback do Google com state na sessão
            with self.client.session_transaction() as sess:
                sess["oauth_state"] = "state_seguro_mock"

            res = self.client.get(
                "/api/auth/google/callback?code=mock_code_123&state=state_seguro_mock"
            )
            # Deve redirecionar para o dashboard após sucesso
            self.assertEqual(res.status_code, 302)
            self.assertIn("/dashboard", res.headers["Location"])

            # Verifica se o usuário Google foi criado
            user_google = Usuario.query.filter_by(google_id="google_oauth_id_98765").first()
            self.assertIsNotNone(user_google)
            self.assertEqual(user_google.email, "google_usuario@teste.com")
            self.assertEqual(user_google.nome, "Maria Google")

            # Verifica o provisionamento automático da carteira inicial e das 10 categorias canônicas
            contas = Conta.query.filter_by(usuario_id=user_google.id).all()
            self.assertEqual(len(contas), 1)
            self.assertEqual(contas[0].nome, "Carteira")

            categorias = Categoria.query.filter_by(usuario_id=user_google.id).all()
            self.assertEqual(len(categorias), 10)

            # Verifica que a sessão foi inicializada com o novo usuário
            res_sessao = self.client.get("/api/auth/sessao")
            self.assertEqual(res_sessao.status_code, 200)
            self.assertTrue(res_sessao.get_json()["autenticado"])
            self.assertEqual(
                res_sessao.get_json()["dados"]["usuario"]["email"],
                "google_usuario@teste.com",
            )

            # Testa cancelamento do Google (usuário clicou em cancelar no consentimento)
            res_cancel = self.client.get("/api/auth/google/callback?error=access_denied")
            self.assertEqual(res_cancel.status_code, 302)
            self.assertIn("google_auth_cancelado", res_cancel.headers["Location"])


if __name__ == "__main__":
    unittest.main()

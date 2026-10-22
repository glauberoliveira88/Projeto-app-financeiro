"""Suíte de testes automatizados da Fase 12 — Revisão de Segurança, Validação Final e Preparação para Deploy.

Conforme docs/FSD.md (Seções 3, 5, 7, 8, 9, 14, 15, 16, 19, 20, 21, 22, 23, 24 e 26):
1. Isolamento rigoroso por usuario_id em todas as rotas (prevenção contra IDOR e HTTP 403 / 404);
2. Defesa contra força bruta de login (5 falhas -> bloqueio temporário por 15 min e log em logs_seguranca);
3. Proteção contra CSRF em requisições de mutação de estado (POST, PUT, PATCH, DELETE);
4. Mecanismo resiliente de contingência de logs em logs/error.log com fallback caso o MySQL falhe;
5. Mensagens de erro seguras para o usuário final sem vazamento de stack traces ou detalhes técnicos;
6. Políticas de integridade de senha (mínimo 8 caracteres, hashing com salt);
7. Sanitização contra injeção e XSS em entradas de texto;
8. Verificação de conformidade estrita de escopo (sem uploads, sem OFX/Open Finance, sem exportação externa, sem moedas estrangeiras);
9. Verificação de ausência de arquivos .env e integridade de configuração em código Python.
"""
import unittest
import os
import glob
from decimal import Decimal
from datetime import datetime, date, timedelta, timezone
from unittest.mock import patch, MagicMock
from flask import session

from app import create_app
from app.models import (
    db,
    Usuario,
    Conta,
    Categoria,
    Lancamento,
    LancamentoRecorrente,
    LogErro,
    LogSeguranca,
)
from app.services.logger_service import registrar_erro, registrar_seguranca
from config.config import Config


class SecurityTestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class Fase12SegurancaEValidacaoTestCase(unittest.TestCase):
    """Bateria completa de validação de segurança e integridade do FinançasSimples."""

    def setUp(self):
        self.app = create_app(SecurityTestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Cria 2 usuários para validação de tenant isolation / anti-IDOR
        self.user_a = Usuario(nome="Alice Santos", email="alice@teste.com", tema_preferido="dark")
        self.user_a.definir_senha("SenhaForte123")

        self.user_b = Usuario(nome="Bob Lima", email="bob@teste.com", tema_preferido="light")
        self.user_b.definir_senha("SenhaForte123")

        db.session.add_all([self.user_a, self.user_b])
        db.session.commit()

        # Provisiona contas e categorias para ambos os usuários
        self.conta_a = Conta(usuario_id=self.user_a.id, nome="Carteira Alice", saldo_inicial=Decimal("1000.00"))
        self.cat_a_rec = Categoria(usuario_id=self.user_a.id, nome="Salário Alice", tipo="receita")
        self.cat_a_desp = Categoria(usuario_id=self.user_a.id, nome="Alimentação Alice", tipo="despesa", teto_orcamento=Decimal("500.00"))

        self.conta_b = Conta(usuario_id=self.user_b.id, nome="Carteira Bob", saldo_inicial=Decimal("2000.00"))
        self.cat_b_rec = Categoria(usuario_id=self.user_b.id, nome="Salário Bob", tipo="receita")
        self.cat_b_desp = Categoria(usuario_id=self.user_b.id, nome="Alimentação Bob", tipo="despesa", teto_orcamento=Decimal("800.00"))

        db.session.add_all([self.conta_a, self.cat_a_rec, self.cat_a_desp, self.conta_b, self.cat_b_rec, self.cat_b_desp])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def autenticar(self, usuario):
        """Injeta o usuario_id na sessão para chamadas subsequentes do test_client."""
        with self.client.session_transaction() as sess:
            sess["usuario_id"] = usuario.id

    def test_01_isolamento_contas_anti_idor(self):
        """Valida que um usuário não pode acessar, editar, arquivar, reativar ou excluir contas alheias."""
        self.autenticar(self.user_a)

        # Alice tenta ler contas (deve listar apenas as suas)
        res = self.client.get("/api/contas")
        self.assertEqual(res.status_code, 200)
        contas_retornadas = res.get_json()["dados"]["contas"]
        ids_contas = [c["id"] for c in contas_retornadas]
        self.assertIn(self.conta_a.id, ids_contas)
        self.assertNotIn(self.conta_b.id, ids_contas)

        # Alice tenta editar a conta de Bob (HTTP 404 / 403)
        res = self.client.put(f"/api/contas/{self.conta_b.id}", json={"nome": "Conta Hackeada"})
        self.assertIn(res.status_code, [403, 404])

        # Alice tenta arquivar a conta de Bob
        res = self.client.patch(f"/api/contas/{self.conta_b.id}/arquivar")
        self.assertIn(res.status_code, [403, 404])

        # Alice tenta reativar a conta de Bob
        res = self.client.patch(f"/api/contas/{self.conta_b.id}/reativar")
        self.assertIn(res.status_code, [403, 404])

        # Alice tenta excluir a conta de Bob
        res = self.client.delete(f"/api/contas/{self.conta_b.id}")
        self.assertIn(res.status_code, [403, 404])

    def test_02_isolamento_categorias_anti_idor(self):
        """Valida que um usuário não pode ler, editar, arquivar ou reatribuir categorias de outro usuário."""
        self.autenticar(self.user_a)

        # Alice tenta listar categorias (deve listar apenas as suas)
        res = self.client.get("/api/categorias")
        self.assertEqual(res.status_code, 200)
        cats = res.get_json()["dados"]["categorias"]
        ids_cats = [c["id"] for c in cats]
        self.assertIn(self.cat_a_desp.id, ids_cats)
        self.assertNotIn(self.cat_b_desp.id, ids_cats)

        # Alice tenta editar categoria de Bob
        res = self.client.put(f"/api/categorias/{self.cat_b_desp.id}", json={"nome": "Tentativa Invasão"})
        self.assertIn(res.status_code, [403, 404])

        # Alice tenta excluir categoria de Bob
        res = self.client.delete(f"/api/categorias/{self.cat_b_desp.id}")
        self.assertIn(res.status_code, [403, 404])

        # Alice tenta reatribuir usando categoria de Bob como destino
        res = self.client.post(
            f"/api/categorias/{self.cat_a_desp.id}/reatribuir-excluir",
            json={"nova_categoria_id": self.cat_b_desp.id}
        )
        self.assertIn(res.status_code, [400, 403, 404])

    def test_03_isolamento_lancamentos_anti_idor(self):
        """Valida que um usuário não pode criar lançamentos usando recursos de outro usuário, nem manipular lançamentos alheios."""
        # Cria lançamento legítimo para Bob
        lanc_bob = Lancamento(
            usuario_id=self.user_b.id,
            conta_id=self.conta_b.id,
            categoria_id=self.cat_b_desp.id,
            tipo="despesa",
            valor=Decimal("150.00"),
            data_competencia=date.today(),
            data_vencimento=date.today(),
            descricao="Despesa de Bob",
            status="pago"
        )
        db.session.add(lanc_bob)
        db.session.commit()

        # Alice autenticada
        self.autenticar(self.user_a)

        # 1. Alice tenta criar lançamento associando conta de Bob
        res = self.client.post("/api/lancamentos", json={
            "tipo": "despesa",
            "valor": "50.00",
            "data_competencia": str(date.today()),
            "data_vencimento": str(date.today()),
            "descricao": "Tentativa com conta alheia",
            "categoria_id": self.cat_a_desp.id,
            "conta_id": self.conta_b.id,
            "status": "pago"
        })
        self.assertIn(res.status_code, [400, 403, 404])

        # 2. Alice tenta criar lançamento associando categoria de Bob
        res = self.client.post("/api/lancamentos", json={
            "tipo": "despesa",
            "valor": "50.00",
            "data_competencia": str(date.today()),
            "data_vencimento": str(date.today()),
            "descricao": "Tentativa com categoria alheia",
            "categoria_id": self.cat_b_desp.id,
            "conta_id": self.conta_a.id,
            "status": "pago"
        })
        self.assertIn(res.status_code, [400, 403, 404])

        # 3. Alice tenta criar transferência usando conta de Bob como origem ou destino
        res = self.client.post("/api/lancamentos/transferencia", json={
            "valor": "100.00",
            "data_competencia": str(date.today()),
            "conta_origem_id": self.conta_a.id,
            "conta_destino_id": self.conta_b.id,
            "descricao": "Transferência para conta alheia"
        })
        self.assertIn(res.status_code, [400, 403, 404])

        # 4. Alice tenta ler/editar/liquidar/excluir lançamento de Bob
        res = self.client.put(f"/api/lancamentos/{lanc_bob.id}", json={"descricao": "Tentativa de alteração"})
        self.assertIn(res.status_code, [403, 404])

        res = self.client.patch(f"/api/lancamentos/{lanc_bob.id}/pagar")
        self.assertIn(res.status_code, [403, 404])

        res = self.client.delete(f"/api/lancamentos/{lanc_bob.id}")
        self.assertIn(res.status_code, [403, 404])

        # Verifica que o lançamento de Bob não foi apagado nem alterado
        db.session.refresh(lanc_bob)
        self.assertIsNone(lanc_bob.deleted_at)
        self.assertEqual(lanc_bob.descricao, "Despesa de Bob")

    def test_04_isolamento_recorrentes_anti_idor(self):
        """Valida que fixos recorrentes pertencem estritamente ao usuário autenticado."""
        fixo_bob = LancamentoRecorrente(
            usuario_id=self.user_b.id,
            conta_id=self.conta_b.id,
            categoria_id=self.cat_b_desp.id,
            tipo="despesa",
            valor=Decimal("200.00"),
            descricao="Aluguel de Bob",
            dia_vencimento=10,
            ativo=True
        )
        db.session.add(fixo_bob)
        db.session.commit()

        self.autenticar(self.user_a)

        # Alice tenta criar modelo vinculando conta ou categoria de Bob
        res = self.client.post("/api/recorrentes", json={
            "tipo": "despesa",
            "valor": "100.00",
            "descricao": "Tentativa Invasão",
            "categoria_id": self.cat_b_desp.id,
            "conta_id": self.conta_a.id,
            "dia_vencimento": 5
        })
        self.assertIn(res.status_code, [400, 403, 404])

        # Alice tenta editar/pausar/excluir o fixo de Bob
        res = self.client.put(f"/api/recorrentes/{fixo_bob.id}", json={"descricao": "Hackeado"})
        self.assertIn(res.status_code, [403, 404])

        res = self.client.patch(f"/api/recorrentes/{fixo_bob.id}/toggle")
        self.assertIn(res.status_code, [403, 404])

        res = self.client.delete(f"/api/recorrentes/{fixo_bob.id}")
        self.assertIn(res.status_code, [403, 404])

    def test_05_protecao_forca_bruta_login(self):
        """Valida bloqueio temporário (15 minutos / HTTP 429) após 5 tentativas de login consecutivas inválidas."""
        # Registra 5 tentativas erradas propositais para a conta de Bob
        ip_teste = "200.150.10.20"
        for i in range(5):
            res = self.client.post("/api/auth/login", json={
                "email": "bob@teste.com",
                "senha": f"SenhaErrada{i}"
            }, environ_base={"REMOTE_ADDR": ip_teste})
            self.assertEqual(res.status_code, 401)
            dados = res.get_json()
            self.assertFalse(dados["sucesso"])

        # A 6ª tentativa deve ser terminantemente bloqueada (HTTP 429 Too Many Requests)
        res_bloqueado = self.client.post("/api/auth/login", json={
            "email": "bob@teste.com",
            "senha": "SenhaForte123"  # Mesmo fornecendo a senha correta, deve estar bloqueado!
        }, environ_base={"REMOTE_ADDR": ip_teste})
        self.assertEqual(res_bloqueado.status_code, 429)
        dados_bloqueio = res_bloqueado.get_json()
        self.assertFalse(dados_bloqueio["sucesso"])
        self.assertIn("15 minuto", dados_bloqueio["erro"])

        # Confirma que um registro de segurança BLOQUEIO_FORCA_BRUTA foi gravado na tabela
        log_seg = LogSeguranca.query.filter_by(evento="BLOQUEIO_FORCA_BRUTA", ip=ip_teste).first()
        self.assertIsNotNone(log_seg)
        self.assertIn("bob@teste.com", log_seg.detalhes)

    def test_06_protecao_csrf_requisicoes_mutadoras(self):
        """Valida a obrigatoriedade do cabeçalho X-CSRFToken quando WTF_CSRF_ENABLED é ativado."""
        # Cria app isolado com CSRF habilitado
        class CsrfTestConfig(Config):
            TESTING = True
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
            WTF_CSRF_ENABLED = True
            CSRF_FORCE_TESTING = True

        app_csrf = create_app(CsrfTestConfig)
        client_csrf = app_csrf.test_client()

        with app_csrf.app_context():
            db.create_all()
            user = Usuario(nome="Carlos", email="carlos@csrf.com")
            user.definir_senha("SenhaForte123")
            db.session.add(user)
            db.session.commit()
            uid = user.id

            # Sem token CSRF em rota mutadora autenticada -> deve ser rejeitada com 400
            with client_csrf.session_transaction() as sess:
                sess["usuario_id"] = uid

            res = client_csrf.post("/api/contas", json={"nome": "Conta Sem CSRF", "saldo_inicial": "100.00"})
            self.assertEqual(res.status_code, 400)
            dados = res.get_json()
            self.assertIn("CSRF", dados.get("erro", ""))

    def test_07_contingencia_de_logs_em_arquivo(self):
        """Valida que falha na gravação do log no MySQL ativa automaticamente a contingência em logs/error.log."""
        log_path = self.app.config.get("LOG_FILE_PATH")
        
        # Garante que o arquivo de log existe ou pode ser escrito
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        if os.path.exists(log_path):
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("")

        # Simula erro de MySQL na gravação do LogErro
        with patch.object(LogErro, "registrar", side_effect=Exception("Simulação de Falha MySQL 2002")):
            resultado = registrar_erro(
                nivel="CRITICAL",
                mensagem="Falha crítica de contingência do teste 12",
                rota="POST /api/lancamentos",
                stack_trace="Traceback detalhado de segurança...",
                ip="10.0.0.5"
            )
            # Retorna False informando que o banco falhou mas acionou o log em arquivo
            self.assertFalse(resultado)

        # Verifica se o arquivo logs/error.log registrou a mensagem de contingência com segurança
        self.assertTrue(os.path.exists(log_path))
        with open(log_path, "r", encoding="utf-8") as f:
            conteudo = f.read()

        self.assertIn("[CONTINGÊNCIA DE LOG]", conteudo)
        self.assertIn("Falha crítica de contingência do teste 12", conteudo)
        self.assertIn("Simulação de Falha MySQL 2002", conteudo)

    def test_08_mensagens_de_erro_seguras_para_usuario(self):
        """Valida que falhas internas não vazam detalhes de infraestrutura ou stack traces (HTTP 500 amigável)."""
        @self.app.route("/api/rota-com-excecao-forcada")
        def rota_falha():
            raise ValueError("Informação confidencial do banco: table financas_simples.usuarios column pass_hash")

        res = self.client.get("/api/rota-com-excecao-forcada")
        self.assertEqual(res.status_code, 500)
        dados = res.get_json()
        self.assertFalse(dados["sucesso"])
        # Garante mensagem amigável sem vazar palavras sensíveis do código
        self.assertIn("Ocorreu um erro interno", dados["erro"])
        self.assertNotIn("Informação confidencial", dados["erro"])
        self.assertNotIn("table financas_simples", dados["erro"])

    def test_09_politica_de_senhas_e_hashing(self):
        """Valida restrição de senha mínima de 8 caracteres e hash forte irreversível com salt."""
        u = Usuario(nome="Teste Senha", email="senha@teste.com")
        
        # Senha com menos de 8 caracteres deve disparar exceção
        with self.assertRaises(ValueError):
            u.definir_senha("1234567")

        # Senha válida deve gerar hash que não contenha a senha em texto puro
        u.definir_senha("MinhaSenhaSegura2026")
        self.assertTrue(u.senha_hash.startswith("scrypt:") or u.senha_hash.startswith("pbkdf2:"))
        self.assertNotIn("MinhaSenhaSegura2026", u.senha_hash)
        self.assertTrue(u.verificar_senha("MinhaSenhaSegura2026"))
        self.assertFalse(u.verificar_senha("SenhaIncorreta"))

    def test_10_sanitizacao_xss_e_caracteres_perigosos(self):
        """Valida sanitização em atualizações de perfil e lançamentos contra XSS."""
        self.autenticar(self.user_a)

        # Tentativa de injetar tag script no nome do perfil
        payload_xss = "<script>alert('xss')</script>Alice Modificada"
        res = self.client.put("/api/usuario/perfil", json={"nome": payload_xss})
        self.assertEqual(res.status_code, 200)
        dados = res.get_json()
        self.assertTrue(dados["sucesso"])
        # Assegura que o script foi neutralizado/sanitizado
        self.assertNotIn("<script>", dados["dados"]["nome"])

    def test_11_conformidade_estrita_de_escopo(self):
        """Valida que nenhum item fora de escopo (uploads, conexões automáticas OFX/bancárias, moedas estrangeiras, exportações) existe."""
        # 1. Verifica todas as regras de rotas registradas no app
        rotas = [str(regra) for regra in self.app.url_map.iter_rules()]

        # Não deve haver rotas de upload ou arquivos
        for r in rotas:
            self.assertNotIn("upload", r.lower())
            self.assertNotIn("exportar", r.lower())
            self.assertNotIn("export", r.lower())
            self.assertNotIn("relatorio-pdf", r.lower())
            self.assertNotIn("csv", r.lower())
            self.assertNotIn("excel", r.lower())
            self.assertNotIn("ofx", r.lower())
            self.assertNotIn("open-finance", r.lower())
            self.assertNotIn("cambio", r.lower())

        # 2. Confirma que não existe nenhum arquivo .env no diretório do projeto
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        arquivos_env = glob.glob(os.path.join(base_dir, "**", ".env*"), recursive=True)
        # Filtra eventuais arquivos dentro do venv se houver
        arquivos_env_proj = [f for f in arquivos_env if "venv" not in f]
        self.assertEqual(len(arquivos_env_proj), 0, f"Arquivo .env proibido encontrado: {arquivos_env_proj}")

    def test_12_protecao_arquivos_htaccess(self):
        """Valida a existência e regras de proteção do arquivo .htaccess para servidores Apache."""
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        htaccess_path = os.path.join(base_dir, ".htaccess")
        self.assertTrue(os.path.exists(htaccess_path), "Arquivo .htaccess não encontrado na raiz")

        with open(htaccess_path, "r", encoding="utf-8") as f:
            conteudo = f.read()

        # Deve conter bloqueio para extensões py, sql, log e pastas sensíveis
        self.assertIn("py", conteudo)
        self.assertIn("sql", conteudo)
        self.assertIn("log", conteudo)
        self.assertIn("Require all denied", conteudo)
        self.assertIn("config", conteudo)
        self.assertIn("database", conteudo)


if __name__ == "__main__":
    unittest.main()

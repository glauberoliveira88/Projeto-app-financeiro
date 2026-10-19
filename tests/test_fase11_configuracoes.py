"""Suíte de testes automatizados para a Fase 11 — Módulo de Configurações, Perfil e Alternância de Tema.

Conforme docs/FSD.md (Seções 6.1, 11.1, 12.9, 13.8, 14.1 e 15) e docs/DESIGN.md:
- Valida o endpoint GET /api/usuario/perfil (consulta segura de dados cadastrais);
- Valida o endpoint PUT/PATCH /api/usuario/perfil (atualização e sanitização de nome);
- Valida regras de negócio para nome (2 a 150 caracteres, sanitização HTML contra XSS);
- Valida o endpoint PATCH /api/usuario/tema (persistência da preferência 'dark' ou 'light');
- Valida rejeição HTTP 400 para temas inválidos;
- Valida isolamento e proteção contra IDOR (apenas os dados da sessão ativa são manipulados);
- Valida exigência de autenticação (@login_required / HTTP 401 para requisições anônimas).
"""
import unittest
from app import create_app
from app.models import db, Usuario
from config.config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ConfiguracoesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Criação de 2 usuários para testes de isolamento
        self.user1 = Usuario(nome="Arthur Silva", email="arthur@teste.com", tema_preferido="dark")
        self.user1.definir_senha("SenhaForte123")

        self.user2 = Usuario(nome="Carlos Souza", email="carlos@teste.com", tema_preferido="light")
        self.user2.definir_senha("SenhaForte123")

        db.session.add_all([self.user1, self.user2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def autenticar(self, usuario):
        """Simula login seguro injetando o usuario_id na sessão do test_client."""
        with self.client.session_transaction() as sess:
            sess["usuario_id"] = usuario.id

    def test_01_obter_perfil_sem_autenticacao(self):
        """Requisição anônima a GET /api/usuario/perfil deve retornar HTTP 401."""
        res = self.client.get("/api/usuario/perfil")
        self.assertEqual(res.status_code, 401)
        dados = res.get_json()
        self.assertFalse(dados["sucesso"])
        self.assertIn("erro", dados)

    def test_02_obter_perfil_autenticado(self):
        """GET /api/usuario/perfil deve retornar os dados cadastrais do usuário da sessão."""
        self.autenticar(self.user1)
        res = self.client.get("/api/usuario/perfil")
        self.assertEqual(res.status_code, 200)

        dados = res.get_json()
        self.assertTrue(dados["sucesso"])
        perfil = dados["dados"]
        self.assertEqual(perfil["id"], self.user1.id)
        self.assertEqual(perfil["nome"], "Arthur Silva")
        self.assertEqual(perfil["email"], "arthur@teste.com")
        self.assertEqual(perfil["tema_preferido"], "dark")
        self.assertFalse(perfil["is_google_user"])
        # Não deve expor senha_hash ou tokens de recuperação
        self.assertNotIn("senha_hash", perfil)
        self.assertNotIn("token_recuperacao", perfil)

    def test_03_atualizar_nome_perfil_sucesso(self):
        """PUT /api/usuario/perfil deve atualizar o nome no banco e retornar os dados."""
        self.autenticar(self.user1)
        res = self.client.put("/api/usuario/perfil", json={"nome": "Arthur Silva Atualizado"})
        self.assertEqual(res.status_code, 200)

        dados = res.get_json()
        self.assertTrue(dados["sucesso"])
        self.assertEqual(dados["dados"]["nome"], "Arthur Silva Atualizado")

        # Verifica persistência no banco
        user_db = db.session.get(Usuario, self.user1.id)
        self.assertEqual(user_db.nome, "Arthur Silva Atualizado")

    def test_04_atualizar_nome_validacoes(self):
        """PUT /api/usuario/perfil deve validar campos vazios, tamanho mínimo e máximo."""
        self.autenticar(self.user1)

        # 1. Sem campo nome
        res = self.client.put("/api/usuario/perfil", json={})
        self.assertEqual(res.status_code, 400)

        # 2. Nome muito curto (< 2 caracteres)
        res = self.client.put("/api/usuario/perfil", json={"nome": "A"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("mínimo 2 caracteres", res.get_json()["erro"])

        # 3. Nome composto apenas de espaços
        res = self.client.put("/api/usuario/perfil", json={"nome": "   "})
        self.assertEqual(res.status_code, 400)

        # 4. Nome muito longo (> 150 caracteres)
        nome_longo = "A" * 151
        res = self.client.put("/api/usuario/perfil", json={"nome": nome_longo})
        self.assertEqual(res.status_code, 400)
        self.assertIn("não pode exceder 150 caracteres", res.get_json()["erro"])

    def test_05_atualizar_nome_sanitizacao_html(self):
        """PUT /api/usuario/perfil deve sanitizar tags HTML para prevenir XSS armazenado."""
        self.autenticar(self.user1)
        payload = {"nome": "Arthur <script>alert('xss')</script>"}
        res = self.client.put("/api/usuario/perfil", json=payload)
        self.assertEqual(res.status_code, 200)

        user_db = db.session.get(Usuario, self.user1.id)
        self.assertNotIn("<script>", user_db.nome)
        self.assertIn("&lt;script&gt;", user_db.nome)

    def test_06_atualizar_tema_dark_e_light(self):
        """PATCH /api/usuario/tema deve alterar e persistir 'dark' e 'light'."""
        self.autenticar(self.user1)

        # Altera para 'light'
        res = self.client.patch("/api/usuario/tema", json={"tema": "light"})
        self.assertEqual(res.status_code, 200)
        dados = res.get_json()
        self.assertTrue(dados["sucesso"])
        self.assertEqual(dados["dados"]["tema_preferido"], "light")

        user_db = db.session.get(Usuario, self.user1.id)
        self.assertEqual(user_db.tema_preferido, "light")

        # Altera de volta para 'dark'
        res = self.client.patch("/api/usuario/tema", json={"tema": "dark"})
        self.assertEqual(res.status_code, 200)
        user_db = db.session.get(Usuario, self.user1.id)
        self.assertEqual(user_db.tema_preferido, "dark")

    def test_07_atualizar_tema_invalido(self):
        """PATCH /api/usuario/tema com valor inválido deve retornar HTTP 400."""
        self.autenticar(self.user1)

        # Tema inexistente
        res = self.client.patch("/api/usuario/tema", json={"tema": "azul"})
        self.assertEqual(res.status_code, 400)
        dados = res.get_json()
        self.assertFalse(dados["sucesso"])
        self.assertIn("Tema inválido", dados["erro"])

        # Tema vazio ou numérico
        res_vazio = self.client.patch("/api/usuario/tema", json={"tema": ""})
        self.assertEqual(res_vazio.status_code, 400)

        # O tema do usuário permanece inalterado
        user_db = db.session.get(Usuario, self.user1.id)
        self.assertEqual(user_db.tema_preferido, "dark")

    def test_08_isolamento_de_dados_anti_idor(self):
        """As operações em /api/usuario/* devem afetar estritamente o usuário autenticado."""
        # Autentica como user1
        self.autenticar(self.user1)
        self.client.put("/api/usuario/perfil", json={"nome": "Arthur Modificado"})
        self.client.patch("/api/usuario/tema", json={"tema": "light"})

        # Dados do user2 não podem ter sido afetados
        user2_db = db.session.get(Usuario, self.user2.id)
        self.assertEqual(user2_db.nome, "Carlos Souza")
        self.assertEqual(user2_db.tema_preferido, "light")

        # Autentica como user2 e verifica seu perfil
        self.autenticar(self.user2)
        res_u2 = self.client.get("/api/usuario/perfil")
        self.assertEqual(res_u2.status_code, 200)
        self.assertEqual(res_u2.get_json()["dados"]["nome"], "Carlos Souza")

    def test_09_tema_preferido_retornado_em_login_e_sessao(self):
        """Endpoints /api/auth/login e /api/auth/sessao devem retornar tema_preferido do usuário."""
        # Login tradicional
        res_login = self.client.post("/api/auth/login", json={"email": "carlos@teste.com", "senha": "SenhaForte123"})
        self.assertEqual(res_login.status_code, 200)
        dados_login = res_login.get_json()
        self.assertTrue(dados_login["sucesso"])
        self.assertEqual(dados_login["usuario"]["tema_preferido"], "light")

        # Consulta de sessão ativa
        res_sessao = self.client.get("/api/auth/sessao")
        self.assertEqual(res_sessao.status_code, 200)
        dados_sessao = res_sessao.get_json()
        self.assertTrue(dados_sessao["autenticado"])
        self.assertEqual(dados_sessao["usuario"]["tema_preferido"], "light")

    def test_10_renderizacao_html_injeta_tema_preferido_do_usuario(self):
        """O servidor deve injetar data-theme='light' no html para usuário logado com preferência light."""
        # 1. Usuário não autenticado -> padrão 'dark'
        res_anon = self.client.get("/")
        self.assertEqual(res_anon.status_code, 200)
        html_anon = res_anon.get_data(as_text=True)
        self.assertIn('data-theme="dark"', html_anon)
        self.assertNotIn('light-theme', html_anon.split("<head>")[0])

        # 2. Usuário 2 autenticado (preferência 'light')
        self.autenticar(self.user2)
        res_auth = self.client.get("/dashboard")
        self.assertEqual(res_auth.status_code, 200)
        html_auth = res_auth.get_data(as_text=True)
        self.assertIn('data-theme="light"', html_auth)
        self.assertIn('class="light-theme"', html_auth)

    def test_11_script_sincronizacao_tema_presente_no_html(self):
        """O template index.html deve conter o script de sincronização de tema no head."""
        res = self.client.get("/")
        html = res.get_data(as_text=True)
        self.assertIn("financas_tema", html)
        self.assertIn("serverTheme", html)


if __name__ == "__main__":
    unittest.main()

"""Testes automatizados da Fase 5 — Shell Base da Interface (docs/PLANO.md e docs/DESIGN.md).

Valida:
1. Renderização do template index.html com injeção do token CSRF e montagem do React;
2. Disponibilidade e conformidade dos assets do Design Obsidian (CSS, JS, Logos e Vendor);
3. Validação do utilitário de CSRF (geração, validação e proteção em mutações);
4. Roteamento das páginas web do shell (SPA / History API).
"""
import re
import unittest
from flask import session
from app import create_app
from app.utils.csrf import gerar_csrf_token, validar_csrf_token


class TestFase5Interface(unittest.TestCase):
    """Suíte de testes para a Fase 5 — Shell Base da Interface."""

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
        self.client = self.app.test_client()

    def test_renderizacao_index_html_e_meta_csrf(self):
        """Valida se o template base é servido na rota raiz com a meta tag de CSRF injetada."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # 1. Deve conter declaração HTML5 e doctype
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn('<div id="root"></div>', html)

        # 2. Deve conter a meta tag csrf-token com valor hexadecimal de 64 caracteres (32 bytes)
        match = re.search(r'<meta\s+name=["\']csrf-token["\']\s+content=["\']([a-f0-9]{64})["\']', html)
        self.assertIsNotNone(match, "Meta tag csrf-token com token válido não foi encontrada no HTML.")

        # 3. Deve referenciar folha de estilos e bibliotecas locais
        self.assertIn("/static/css/style.css", html)
        self.assertIn("/static/js/vendor/react.production.min.js", html)
        self.assertIn("/static/js/vendor/react-dom.production.min.js", html)
        self.assertIn("/static/js/vendor/babel.min.js", html)
        self.assertIn("/static/js/api.js", html)
        self.assertIn("/static/js/app.js", html)

    def test_rotas_web_renderizam_shell(self):
        """Valida se todas as rotas web públicas e SPA renderizam o index.html com sucesso."""
        rotas = ["/login", "/cadastro", "/recuperar-senha", "/redefinir-senha/token-teste-123", "/lancamentos", "/contas"]
        for rota in rotas:
            resp = self.client.get(rota)
            self.assertEqual(resp.status_code, 200, f"Falha ao renderizar {rota}")
            self.assertIn('<div id="root"></div>', resp.get_data(as_text=True))
            self.assertIn('name="csrf-token"', resp.get_data(as_text=True))

    def test_entrega_e_conteudo_css_obsidian(self):
        """Valida se o style.css é servido e cumpre as especificações do docs/DESIGN.md."""
        resp = self.client.get("/static/css/style.css")
        self.assertEqual(resp.status_code, 200)
        css = resp.get_data(as_text=True)

        # Validação das cores oficiais do Obsidian High-Contrast Dark
        self.assertIn("#09090b", css)  # Background near-black
        self.assertIn("#a78bfa", css)  # Primário violeta suave
        self.assertIn("#34d399", css)  # Terciário verde esmeralda
        self.assertIn("#ef4444", css)  # Vermelho de erro
        self.assertIn("Geist", css)    # Família de fontes oficial
        self.assertIn("light-theme", css) # Variação de tema claro

    def test_entrega_e_scripts_locais(self):
        """Valida se todos os scripts JS locais do vendor e da aplicação estão disponíveis."""
        scripts = [
            "/static/js/api.js",
            "/static/js/app.js",
            "/static/js/vendor/react.production.min.js",
            "/static/js/vendor/react-dom.production.min.js",
            "/static/js/vendor/babel.min.js",
        ]
        for script in scripts:
            resp = self.client.get(script)
            self.assertEqual(resp.status_code, 200, f"Script não encontrado: {script}")
            self.assertGreater(len(resp.data), 0, f"Script vazio: {script}")

    def test_entrega_logotipos_oficiais(self):
        """Valida se as logotipos oficiais do tema claro e escuro são servidas."""
        resp_dark = self.client.get("/static/img/logo_tema_escuro.png")
        self.assertEqual(resp_dark.status_code, 200)

        resp_light = self.client.get("/static/img/logo_tema_claro.png")
        self.assertEqual(resp_light.status_code, 200)

    def test_protecao_csrf_bloqueia_mutacao_sem_token(self):
        """Valida se mutações POST sem token CSRF são bloqueadas quando CSRF_FORCE_TESTING está ativo."""
        self.app.config["CSRF_FORCE_TESTING"] = True
        try:
            # Requisição POST sem cabeçalho X-CSRFToken
            resp = self.client.post("/api/auth/login", json={"email": "teste@teste.com", "senha": "qualquersenhainvalida"})
            self.assertEqual(resp.status_code, 400)
            dados = resp.get_json()
            self.assertFalse(dados["sucesso"])
            self.assertEqual(dados.get("codigo"), "CSRF_INVALIDO")
        finally:
            self.app.config["CSRF_FORCE_TESTING"] = False

    def test_protecao_csrf_permite_mutacao_com_token_valido(self):
        """Valida se mutações com cabeçalho X-CSRFToken correto passam pela barreira CSRF."""
        self.app.config["CSRF_FORCE_TESTING"] = True
        try:
            # 1. Carrega a página inicial para inicializar a sessão e obter o token CSRF
            resp_index = self.client.get("/")
            html = resp_index.get_data(as_text=True)
            match = re.search(r'name=["\']csrf-token["\']\s+content=["\']([a-f0-9]{64})["\']', html)
            token = match.group(1)

            # 2. Realiza requisição POST anexando X-CSRFToken
            resp = self.client.post(
                "/api/auth/cadastro",
                json={"nome": ""},
                headers={"X-CSRFToken": token},
            )
            # A requisição deve passar pelo middleware CSRF (não retorna CSRF_INVALIDO)
            dados = resp.get_json()
            self.assertNotEqual(dados.get("codigo"), "CSRF_INVALIDO")
            self.assertEqual(resp.status_code, 400)
            self.assertIn("O nome completo é obrigatório", dados.get("erro", ""))
        finally:
            self.app.config["CSRF_FORCE_TESTING"] = False



if __name__ == "__main__":
    unittest.main()

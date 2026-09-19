"""Utilitário de Proteção contra CSRF (docs/FSD.md - Seções 5 e 19.3).

Gera tokens CSRF criptograficamente seguros para injeção no template index.html
e valida a presença do cabeçalho X-CSRFToken em requisições de mutação de estado.
"""
import secrets
from flask import current_app, jsonify, request, session


def gerar_csrf_token() -> str:
    """Gera ou recupera o token CSRF vinculado à sessão atual."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]


def validar_csrf_token(token: str) -> bool:
    """Valida o token CSRF recebido contra o armazenado na sessão do usuário."""
    token_esperado = session.get("_csrf_token")
    if not token_esperado or not token:
        return False
    return secrets.compare_digest(str(token_esperado), str(token))


def verificar_csrf():
    """Middleware executado antes de cada requisição para validar CSRF em mutações."""
    # Métodos idempotentes / de leitura não necessitam de validação CSRF
    if request.method in ("GET", "HEAD", "OPTIONS", "TRACE"):
        return None

    # Se a aplicação estiver em modo de teste e não for forçada a verificação
    if current_app.config.get("TESTING") and not current_app.config.get("CSRF_FORCE_TESTING", False):
        return None

    if not current_app.config.get("CSRF_PROTECT", True):
        return None

    # Extrai o token do cabeçalho X-CSRFToken / X-CSRF-Token ou do corpo json/form
    token = request.headers.get("X-CSRFToken") or request.headers.get("X-CSRF-Token")
    if not token and request.is_json and request.get_json(silent=True):
        token = request.get_json(silent=True).get("csrf_token")
    if not token and request.form:
        token = request.form.get("csrf_token")

    if not token or not validar_csrf_token(token):
        return jsonify({
            "sucesso": False,
            "erro": "Token CSRF inválido ou ausente. Recarregue a página e tente novamente.",
            "codigo": "CSRF_INVALIDO",
        }), 400

    return None


def renovar_sessao_mantendo_csrf(usuario_id: int) -> str:
    """Regenera a sessão para prevenção de Session Fixation preservando o token CSRF."""
    token = session.get("_csrf_token") or secrets.token_hex(32)
    session.clear()
    session["_csrf_token"] = token
    session["usuario_id"] = usuario_id
    session.permanent = True
    return token


def init_csrf(app):
    """Inicializa a proteção CSRF na aplicação Flask."""
    # Disponibiliza csrf_token() nos templates Jinja2
    app.jinja_env.globals["csrf_token"] = gerar_csrf_token

    # Registra interceptor de validação antes da execução dos controllers
    app.before_request(verificar_csrf)

    # Rota auxiliar para obtenção ou sincronização de CSRF token
    @app.route("/api/auth/csrf", methods=["GET"])
    def api_obter_csrf():
        return jsonify({
            "sucesso": True,
            "csrf_token": gerar_csrf_token(),
        }), 200


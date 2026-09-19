"""Application Factory do FinançasSimples (docs/FSD.md - Seções 3, 5 e 19).

Inicializa a aplicação Flask, extensões (SQLAlchemy), configuração de logging
resiliente e manipuladores globais de erro com contingência.
"""
import os
import logging
import traceback
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
from config.config import Config
from app.models import db


def create_app(config_class=Config):
    """Application Factory principal."""

    # Caminhos base da aplicação
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    template_dir = os.path.join(base_dir, "app", "templates")
    static_dir = os.path.join(base_dir, "app", "static")

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
        static_url_path="/static",
    )

    app.config.from_object(config_class)

    # 1. Configuração do Mecanismo de Contingência de Logs em Arquivo
    configurar_logs(app)

    # 2. Inicialização da Extensão SQLAlchemy (Fase 3)
    db.init_app(app)

    # 3. Proteção e Injeção de CSRF Token (Fase 5)
    from app.utils.csrf import init_csrf
    init_csrf(app)

    # 4. Registro dos Manipuladores Globais de Erro
    registrar_error_handlers(app)

    # 5. Contexto de Sessão e Usuário Autenticado (Fase 4)
    from app.utils.auth import obter_usuario_atual
    @app.before_request
    def carregar_usuario():
        obter_usuario_atual()

    # 6. Registro de Blueprints / Controllers
    from app.controllers import auth_bp
    app.register_blueprint(auth_bp)

    # Rota raiz servindo o shell da aplicação
    @app.route("/", methods=["GET"])
    def index():
        from flask import render_template
        return render_template("index.html")

    # Rotas web do shell (SPA / History API)
    @app.route("/lancamentos", methods=["GET"])
    @app.route("/contas", methods=["GET"])
    @app.route("/categorias", methods=["GET"])
    @app.route("/recorrentes", methods=["GET"])
    @app.route("/configuracoes", methods=["GET"])
    def spa_routes():
        from flask import render_template
        return render_template("index.html")

    # Rota básica de verificação de saúde da aplicação
    @app.route("/api/health", methods=["GET"])
    def health_check():
        db_status = "desconectado"
        try:
            db.session.execute(db.text("SELECT 1"))
            db_status = "operacional"
        except Exception as e:
            db_status = f"falha: {str(e)}"

        return jsonify({
            "sucesso": True,
            "sistema": "FinançasSimples",
            "fase": "Fase 5 - Shell Base da Interface (Design Obsidian, CSS, Meta CSRF e Casca React)",
            "banco_de_dados": db_status,
            "status": "ok",
        }), 200

    return app


def configurar_logs(app):
    """Configura o mecanismo de contingência de logs em arquivo protegido."""
    log_path = app.config.get("LOG_FILE_PATH")
    if app.config.get("LOG_TO_FILE") and log_path:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_path, maxBytes=1024 * 1024 * 5, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s in %(pathname)s:%(lineno)d: %(message)s"
            )
        )
        file_handler.setLevel(logging.INFO if not app.debug else logging.DEBUG)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO if not app.debug else logging.DEBUG)


def registrar_error_handlers(app):
    """Registra capturadores centralizados de erro HTTP e exceções não tratadas (docs/FSD.md - Seção 19.1)."""
    from app.services.logger_service import registrar_erro

    @app.errorhandler(400)
    def bad_request_error(e):
        return jsonify({
            "sucesso": False,
            "erro": "Requisição inválida ou parâmetros ausentes.",
        }), 400

    @app.errorhandler(403)
    def forbidden_error(e):
        return jsonify({
            "sucesso": False,
            "erro": "Acesso negado. Você não tem permissão para acessar este recurso.",
        }), 403

    @app.errorhandler(404)
    def not_found_error(e):
        return jsonify({
            "sucesso": False,
            "erro": "Recurso não encontrado.",
        }), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        tb = traceback.format_exc()
        rota = f"{request.method} {request.path}" if request else None
        ip = request.remote_addr if request else None
        
        # Gravação resiliente (MySQL com fallback para logs/error.log)
        registrar_erro(
            nivel="ERROR",
            mensagem=str(e),
            rota=rota,
            stack_trace=tb,
            ip=ip,
        )

        return jsonify({
            "sucesso": False,
            "erro": "Ocorreu um erro interno ao processar sua solicitação. A equipe técnica já foi notificada. Por favor, tente novamente em instantes.",
        }), 500

    @app.errorhandler(Exception)
    def unhandled_exception_error(e):
        # Captura qualquer exceção geral não mapeada
        tb = traceback.format_exc()
        rota = f"{request.method} {request.path}" if request else None
        ip = request.remote_addr if request else None

        registrar_erro(
            nivel="CRITICAL",
            mensagem=str(e),
            rota=rota,
            stack_trace=tb,
            ip=ip,
        )

        return jsonify({
            "sucesso": False,
            "erro": "Ocorreu um erro interno ao processar sua solicitação. A equipe técnica já foi notificada. Por favor, tente novamente em instantes.",
        }), 500

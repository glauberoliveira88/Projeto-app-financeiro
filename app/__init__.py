import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from config.config import Config


def create_app(config_class=Config):
    """Application Factory do FinançasSimples (docs/FSD.md - Seções 3 e 5)."""
    
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

    # Configuração de Log de Contingência em Arquivo
    configurar_logs(app)

    # Rota básica de verificação de saúde da infraestrutura (Fase 1)
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "ok",
            "sistema": "FinançasSimples",
            "fase": "Fase 1 - Infraestrutura e Base do Projeto Concluída",
            "mensagem": "Servidor Flask operacional e pronto para as próximas fases."
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

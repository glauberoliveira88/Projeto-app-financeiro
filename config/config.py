import os

class Config:
    """Configurações ativas do sistema FinançasSimples (docs/FSD.md - Seção 20.2).
    
    ATENÇÃO: É terminantemente proibido o uso de arquivos .env neste projeto.
    Todas as configurações residem em código Python.
    """
    
    DEBUG = True
    TESTING = False
    
    # Configurações de Conexão com o Banco de Dados MySQL (padrão local XAMPP)
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_NAME = "financas_simples"
    DB_USER = "root"
    DB_PASSWORD = ""
    
    # URI de conexão SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }

    # Parâmetros de Segurança da Aplicação e Sessão Flask
    SECRET_KEY = "dev-secret-key-financas-simples-obsidian-2026"
    SESSION_COOKIE_SECURE = False  # False em desenvolvimento local (HTTP); True em produção (HTTPS)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Credenciais de Integração Google OAuth 2.0
    GOOGLE_CLIENT_ID = ""
    GOOGLE_CLIENT_SECRET = ""
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

    # Parâmetros de Envio de E-mail (SMTP para Recuperação de Senha)
    # Em desenvolvimento local sem SMTP configurado, o link é exibido no console
    MAIL_SERVER = "localhost"
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = "FinançasSimples <noreply@financassimples.local>"

    # Parâmetros de Logs e Diagnóstico com Mecanismo de Contingência
    LOG_TO_FILE = True
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    LOG_FILE_PATH = os.path.join(BASE_DIR, "logs", "error.log")


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

import os

class Config:
    """Configurações centrais do sistema FinançasSimples (docs/FSD.md - Seção 20.2).
    
    ATENÇÃO: O uso de arquivos .env é terminantemente proibido neste projeto.
    Todas as configurações residem em código Python.
    """
    
    # Modo de operação
    DEBUG = False
    TESTING = False
    
    # Configurações de Conexão com o Banco de Dados MySQL
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
    SECRET_KEY = "sua-chave-secreta-de-alta-entropia-aqui"
    SESSION_COOKIE_SECURE = False  # Definir como True em ambiente de produção (HTTPS)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Credenciais de Integração Google OAuth 2.0
    GOOGLE_CLIENT_ID = "seu-google-client-id.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET = "seu-google-client-secret"
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

    # Parâmetros de Envio de E-mail (SMTP para Recuperação de Senha)
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = "FinançasSimples <noreply@financassimples.local>"

    # Parâmetros de Logs e Diagnóstico com Mecanismo de Contingência
    LOG_TO_FILE = True
    # Caminho para arquivo de log de contingência relativo à raiz do projeto
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    LOG_FILE_PATH = os.path.join(BASE_DIR, "logs", "error.log")


class DevelopmentConfig(Config):
    """Configurações para ambiente de desenvolvimento local."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Configurações para ambiente de produção (PythonAnywhere)."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

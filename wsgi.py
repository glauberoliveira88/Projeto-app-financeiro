"""Ponto de entrada WSGI para ambiente de produção (docs/FSD.md - Seção 4 e 5).

Utilizado no PythonAnywhere apontando para este arquivo.
"""
from app import create_app
from config.config import ProductionConfig

application = create_app(ProductionConfig)

if __name__ == "__main__":
    application.run()

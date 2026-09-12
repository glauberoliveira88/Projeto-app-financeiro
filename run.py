"""Ponto de entrada para execução em desenvolvimento local (docs/FSD.md - Seções 4 e 5).

Uso:
    python run.py
"""
from app import create_app
from config.config import DevelopmentConfig

app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    print("Iniciando servidor de desenvolvimento local FinançasSimples...")
    print("Acesse em: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)

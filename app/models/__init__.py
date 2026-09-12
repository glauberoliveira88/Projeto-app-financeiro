"""Módulo central de persistência e modelos ORM do FinançasSimples (docs/FSD.md - Seções 5 e 11).

Disponibiliza a instância central do SQLAlchemy e expõe todos os modelos de dados.
"""
from flask_sqlalchemy import SQLAlchemy

# Instância central do SQLAlchemy (docs/FSD.md - Seções 3 e 5)
db = SQLAlchemy()

# Importação dos modelos para facilitar exportação unificada
from app.models.usuario import Usuario
from app.models.conta import Conta
from app.models.categoria import Categoria
from app.models.lancamento import Lancamento
from app.models.lancamento_recorrente import LancamentoRecorrente
from app.models.log_erro import LogErro
from app.models.log_seguranca import LogSeguranca

__all__ = [
    "db",
    "Usuario",
    "Conta",
    "Categoria",
    "Lancamento",
    "LancamentoRecorrente",
    "LogErro",
    "LogSeguranca",
]

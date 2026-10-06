"""Módulo de Controllers e Blueprints do FinançasSimples (MVC)."""
from app.controllers.auth_controller import auth_bp
from app.controllers.contas_controller import contas_bp
from app.controllers.categorias_controller import categorias_bp
from app.controllers.lancamentos_controller import lancamentos_bp
from app.controllers.recorrentes_controller import recorrentes_bp
from app.controllers.dashboard_controller import dashboard_bp

__all__ = ["auth_bp", "contas_bp", "categorias_bp", "lancamentos_bp", "recorrentes_bp", "dashboard_bp"]


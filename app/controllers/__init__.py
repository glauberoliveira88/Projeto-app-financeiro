"""Módulo de Controllers e Blueprints do FinançasSimples (MVC)."""
from app.controllers.auth_controller import auth_bp
from app.controllers.contas_controller import contas_bp

__all__ = ["auth_bp", "contas_bp"]

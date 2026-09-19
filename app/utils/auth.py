"""Utilitários e Decoradores de Autenticação e Autorização (docs/FSD.md - Seções 8, 9.2, 15 e 16).

Fornece o decorador @login_required, o proxy current_user e a verificação estrita de posse (anti-IDOR).
"""
from functools import wraps
from flask import g, has_request_context, jsonify, redirect, request, session, url_for
from werkzeug.local import LocalProxy
from app.models import Usuario
from app.services.logger_service import registrar_seguranca


def obter_usuario_atual():
    """Retorna o usuário autenticado armazenado na sessão ativa (docs/FSD.md - Seção 15)."""
    if not has_request_context():
        return getattr(g, "current_user", None)

    usuario_id = session.get("usuario_id")
    if not usuario_id:
        g.current_user = None
        return None

    cached_user = getattr(g, "current_user", None)
    if cached_user is not None and getattr(cached_user, "id", None) == usuario_id:
        return cached_user

    from app.models import db
    user = db.session.get(Usuario, usuario_id)
    g.current_user = user
    return user


# Proxy global para o usuário autenticado na requisição atual
current_user = LocalProxy(obter_usuario_atual)


def login_required(f):
    """Decorador para proteção de rotas privadas (FSD Seção 15).
    
    - Requisições para API (/api/* ou aceitando JSON): retorna HTTP 401 Unauthorized;
    - Requisições web normais: redireciona para a tela de login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = obter_usuario_atual()
        if not user:
            # Se for requisição de API ou esperando JSON
            if request.path.startswith("/api/") or request.is_json or "application/json" in request.headers.get("Accept", ""):
                return jsonify({
                    "sucesso": False,
                    "erro": "Autenticação obrigatória para acessar este recurso.",
                }), 401
            # Redirecionamento amigável para interface web
            return redirect(url_for("auth.login_view"))
        return f(*args, **kwargs)

    return decorated_function


def validar_posse(registro, entidade_nome: str = "recurso") -> bool:
    """Valida se o registro pertence estritamente ao usuário autenticado (defesa anti-IDOR).
    
    Caso pertença a outro usuário, registra o incidente na tabela `logs_seguranca`
    e retorna False.
    """
    user = obter_usuario_atual()
    if not user or not registro or registro.usuario_id != user.id:
        ip = request.remote_addr if has_request_context() and request else "127.0.0.1"
        rota = f"{request.method} {request.path}" if has_request_context() and request else None
        rec_id = getattr(registro, "id", "desconhecido")
        dono_id = getattr(registro, "usuario_id", "desconhecido")
        
        registrar_seguranca(
            evento="ACESSO_NEGADO_IDOR",
            ip=ip,
            usuario_id=user.id if user else None,
            detalhes=f"Tentativa de acesso não autorizado ao {entidade_nome} ID={rec_id} (Proprietário={dono_id}) via rota {rota}",
        )
        return False
    return True

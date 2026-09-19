"""Utilitários e Decoradores de Autenticação e Autorização (docs/FSD.md - Seções 8, 9.2, 15 e 16).

Fornece o decorador @login_required, o proxy current_user e a verificação estrita de posse (anti-IDOR).
"""
from functools import wraps
from flask import g, has_request_context, jsonify, redirect, request, session, url_for
from werkzeug.local import LocalProxy
from app.models import Usuario
from app.services.logger_service import registrar_seguranca


class UsuarioAnonimo:
    """Representa um visitante anônimo não autenticado (FSD Seção 15)."""
    id = None
    nome = "Visitante"
    email = None
    is_authenticated = False
    is_active = False
    is_anonymous = True

    def get_id(self):
        return None

    def to_dict(self):
        return None

    def __bool__(self):
        return False


def obter_usuario_atual():
    """Retorna o usuário autenticado armazenado na sessão ativa ou UsuarioAnonimo."""
    if not has_request_context():
        return getattr(g, "current_user", UsuarioAnonimo())

    usuario_id = session.get("usuario_id")
    if not usuario_id:
        anon = UsuarioAnonimo()
        g.current_user = anon
        return anon

    cached_user = getattr(g, "current_user", None)
    if cached_user is not None and getattr(cached_user, "id", None) == usuario_id:
        return cached_user

    from app.models import db
    try:
        user = db.session.get(Usuario, usuario_id)
    except Exception:
        user = None

    if not user:
        anon = UsuarioAnonimo()
        g.current_user = anon
        return anon

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
        if not user or not user.is_authenticated:
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

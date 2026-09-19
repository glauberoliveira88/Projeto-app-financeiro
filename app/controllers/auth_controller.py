"""Controlador de Autenticação e Sessão (docs/FSD.md - Seções 6.1, 13.1, 15, 16, 19.2 e 23).

Implementa as rotas de API para autenticação tradicional (e-mail/senha), recuperação de senha,
proteção contra força bruta, integração com Google OAuth 2.0 e endpoints de sessão.
"""
import re
from flask import (
    Blueprint,
    current_app,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from app.models import db, Usuario
from app.services.auth_service import (
    despachar_email_recuperacao,
    provisionar_dados_iniciais_usuario,
    verificar_bloqueio_forca_bruta,
)
from app.services.logger_service import registrar_erro, registrar_seguranca
from app.utils.auth import current_user, login_required, obter_usuario_atual

auth_bp = Blueprint("auth", __name__)

REGEX_EMAIL = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


def obter_ip_cliente() -> str:
    """Extrai o endereço IP da requisição atual com fallback para localhost."""
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


# ==============================================================================
# Rotas Web (Interface de Autenticação)
# ==============================================================================

@auth_bp.route("/login", methods=["GET"])
def login_view():
    """Exibe a tela de login ou redireciona para o dashboard caso já autenticado."""
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard_view"))
    try:
        return render_template("index.html")
    except Exception:
        # Fallback de inicialização caso index.html ainda não esteja renderizado na Fase 4
        return jsonify({
            "sucesso": True,
            "pagina": "login",
            "mensagem": "Tela de Login do FinançasSimples.",
        }), 200


@auth_bp.route("/cadastro", methods=["GET"])
def cadastro_view():
    """Exibe a tela de cadastro."""
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard_view"))
    try:
        return render_template("index.html")
    except Exception:
        return jsonify({
            "sucesso": True,
            "pagina": "cadastro",
            "mensagem": "Tela de Cadastro do FinançasSimples.",
        }), 200


@auth_bp.route("/recuperar-senha", methods=["GET"])
def recuperar_senha_view():
    """Exibe a tela de solicitação de recuperação de senha."""
    try:
        return render_template("index.html")
    except Exception:
        return jsonify({
            "sucesso": True,
            "pagina": "recuperar-senha",
            "mensagem": "Tela de Recuperação de Senha do FinançasSimples.",
        }), 200


@auth_bp.route("/redefinir-senha/<token>", methods=["GET"])
def redefinir_senha_view(token):
    """Exibe a tela para digitação da nova senha mediante validação do token."""
    usuario = Usuario.query.filter_by(token_recuperacao=token).first()
    token_valido = usuario.validar_token_recuperacao(token) if usuario else False
    try:
        return render_template("index.html", token=token, token_valido=token_valido)
    except Exception:
        return jsonify({
            "sucesso": True,
            "pagina": "redefinir-senha",
            "token": token,
            "token_valido": token_valido,
        }), 200


@auth_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard_view():
    """Ponto de entrada do painel principal autenticado."""
    try:
        return render_template("index.html")
    except Exception:
        return jsonify({
            "sucesso": True,
            "pagina": "dashboard",
            "usuario": current_user.to_dict(),
        }), 200


# ==============================================================================
# Endpoints de API (/api/auth/*)
# ==============================================================================

@auth_bp.route("/api/auth/cadastro", methods=["POST"])
def api_cadastro():
    """Cadastra um novo usuário tradicional e provisiona dados canônicos iniciais (FSD Seção 6.1 e 13.1.1)."""
    dados = request.get_json(silent=True) or {}
    nome = (dados.get("nome") or "").strip()
    email = (dados.get("email") or "").strip().lower()
    senha = dados.get("senha") or ""
    confirmacao = dados.get("confirmacao_senha")

    # 1. Validações básicas de formato e campos obrigatórios
    if not nome or len(nome) < 2 or len(nome) > 150:
        return jsonify({
            "sucesso": False,
            "erro": "O nome completo é obrigatório e deve conter entre 2 e 150 caracteres.",
        }), 400

    if not email or not REGEX_EMAIL.match(email):
        return jsonify({
            "sucesso": False,
            "erro": "Informe um endereço de e-mail válido.",
        }), 400

    if not senha or len(senha) < 8:
        return jsonify({
            "sucesso": False,
            "erro": "A senha deve conter no mínimo 8 caracteres.",
        }), 400

    if confirmacao is not None and senha != confirmacao:
        return jsonify({
            "sucesso": False,
            "erro": "A confirmação de senha não confere.",
        }), 400

    # 2. Verificação de unicidade do e-mail
    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        return jsonify({
            "sucesso": False,
            "erro": "Este endereço de e-mail já está cadastrado.",
        }), 400

    # 3. Criação do usuário e provisionamento canônico em bloco transacional atômico
    try:
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            tema_preferido="dark",
        )
        novo_usuario.definir_senha(senha)
        db.session.add(novo_usuario)
        db.session.flush()  # Obtém o ID gerado para amarrar os provisionamentos

        # Provisiona a carteira padrão inicial ("Carteira") e as 10 categorias canônicas
        provisionar_dados_iniciais_usuario(novo_usuario)
        db.session.commit()

        # 4. Inicializa sessão segura do usuário recém-criado
        session.clear()
        session["usuario_id"] = novo_usuario.id
        session.permanent = True

        registrar_seguranca(
            evento="CADASTRO_SUCESSO",
            ip=obter_ip_cliente(),
            usuario_id=novo_usuario.id,
            detalhes=f"Novo cadastro realizado com sucesso para {email}",
        )

        return jsonify({
            "sucesso": True,
            "mensagem": "Cadastro realizado com sucesso! Bem-vindo(a) ao FinançasSimples.",
            "dados": {
                "usuario": novo_usuario.to_dict(),
            },
        }), 201

    except Exception as e:
        db.session.rollback()
        tb = str(e)
        registrar_erro(
            nivel="ERROR",
            mensagem=f"Falha ao realizar cadastro para o e-mail {email}: {tb}",
            rota="POST /api/auth/cadastro",
            stack_trace=tb,
            ip=obter_ip_cliente(),
        )
        return jsonify({
            "sucesso": False,
            "erro": "Ocorreu um erro ao processar seu cadastro. Por favor, tente novamente.",
        }), 500


@auth_bp.route("/api/auth/login", methods=["POST"])
def api_login():
    """Autentica o usuário tradicional com verificação de hash e proteção contra força bruta (FSD 13.1.2 e 15)."""
    dados = request.get_json(silent=True) or {}
    email = (dados.get("email") or "").strip().lower()
    senha = dados.get("senha") or ""
    ip = obter_ip_cliente()

    if not email or not senha:
        return jsonify({
            "sucesso": False,
            "erro": "E-mail e senha são obrigatórios.",
        }), 400

    # 1. Defesa contra Força Bruta (5 falhas em 15 min -> bloqueio por 15 min)
    bloqueado, minutos_restantes = verificar_bloqueio_forca_bruta(email, ip)
    if bloqueado:
        registrar_seguranca(
            evento="BLOQUEIO_FORCA_BRUTA",
            ip=ip,
            detalhes=f"Tentativa de login bloqueada por força bruta para {email}. Restam {minutos_restantes} minutos.",
        )
        return jsonify({
            "sucesso": False,
            "erro": f"Muitas tentativas incorretas. Seu acesso foi temporariamente bloqueado por {minutos_restantes} minuto(s) para sua segurança.",
        }), 429

    # 2. Busca do usuário e conferência da senha
    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario or not usuario.verificar_senha(senha):
        # Registra o incidente para contagem do bloqueio de força bruta
        registrar_seguranca(
            evento="LOGIN_INVALIDO",
            ip=ip,
            usuario_id=usuario.id if usuario else None,
            detalhes=f"Credenciais incorretas informadas para o e-mail: {email}",
        )
        return jsonify({
            "sucesso": False,
            "erro": "E-mail ou senha incorretos.",
        }), 401

    # 3. Credenciais válidas: inicialização de sessão segura
    session.clear()
    session["usuario_id"] = usuario.id
    session.permanent = True

    registrar_seguranca(
        evento="LOGIN_SUCESSO",
        ip=ip,
        usuario_id=usuario.id,
        detalhes=f"Login realizado com sucesso para {email}",
    )

    return jsonify({
        "sucesso": True,
        "mensagem": "Login efetuado com sucesso.",
        "dados": {
            "usuario": usuario.to_dict(),
        },
    }), 200


@auth_bp.route("/api/auth/logout", methods=["POST", "GET"])
def api_logout():
    """Encerra a sessão ativa do usuário (FSD Seção 15)."""
    user_id = session.get("usuario_id")
    if user_id:
        registrar_seguranca(
            evento="LOGOUT",
            ip=obter_ip_cliente(),
            usuario_id=user_id,
            detalhes="Logout realizado pelo usuário.",
        )
    session.clear()

    # Se a requisição veio via navegador comum (GET /api/auth/logout ou /logout)
    if request.method == "GET":
        return redirect(url_for("auth.login_view"))

    return jsonify({
        "sucesso": True,
        "mensagem": "Sessão encerrada com sucesso.",
    }), 200


@auth_bp.route("/api/auth/sessao", methods=["GET"])
def api_sessao():
    """Retorna o status da sessão ativa do usuário (FSD Seção 15)."""
    user = obter_usuario_atual()
    if user and getattr(user, "is_authenticated", False):
        return jsonify({
            "sucesso": True,
            "autenticado": True,
            "dados": {
                "usuario": user.to_dict(),
            },
        }), 200

    return jsonify({
        "sucesso": True,
        "autenticado": False,
        "dados": None,
    }), 200


@auth_bp.route("/api/auth/protegido-teste", methods=["GET"])
@login_required
def api_protegido_teste():
    """Endpoint de teste para validação de autorização via @login_required (FSD Seção 15)."""
    return jsonify({
        "sucesso": True,
        "mensagem": "Acesso autorizado ao recurso protegido.",
        "dados": {
            "usuario": current_user.to_dict(),
        },
    }), 200


@auth_bp.route("/api/auth/recuperar-senha", methods=["POST"])
def api_recuperar_senha():
    """Gera token temporário e despacha instruções de recuperação (FSD Seções 6.1 e 15)."""
    dados = request.get_json(silent=True) or {}
    email = (dados.get("email") or "").strip().lower()
    ip = obter_ip_cliente()

    if not email or not REGEX_EMAIL.match(email):
        return jsonify({
            "sucesso": False,
            "erro": "Informe um endereço de e-mail válido.",
        }), 400

    usuario = Usuario.query.filter_by(email=email).first()

    # Mensagem padronizada e segura (sem expor se o e-mail existe, mitigando enumeração de contas)
    msg_sucesso = (
        "Se o e-mail informado estiver cadastrado em nosso sistema, as instruções para "
        "redefinição de senha foram enviadas."
    )

    if usuario:
        token = usuario.gerar_token_recuperacao(horas_validade=1)
        db.session.commit()

        registrar_seguranca(
            evento="RECUPERACAO_SENHA_SOLICITADA",
            ip=ip,
            usuario_id=usuario.id,
            detalhes=f"Link de recuperação gerado para {email}",
        )

        # Envia e-mail ou exibe no console/log de desenvolvimento
        despachar_email_recuperacao(usuario, token)

    return jsonify({
        "sucesso": True,
        "mensagem": msg_sucesso,
    }), 200


@auth_bp.route("/api/auth/redefinir-senha", methods=["POST"])
def api_redefinir_senha():
    """Redefine a senha do usuário mediante validação do token temporário (FSD Seção 15)."""
    dados = request.get_json(silent=True) or {}
    token = (dados.get("token") or "").strip()
    nova_senha = dados.get("nova_senha") or ""
    confirmacao = dados.get("confirmacao_senha")
    ip = obter_ip_cliente()

    if not token:
        return jsonify({
            "sucesso": False,
            "erro": "O token de recuperação é obrigatório.",
        }), 400

    if not nova_senha or len(nova_senha) < 8:
        return jsonify({
            "sucesso": False,
            "erro": "A nova senha deve conter no mínimo 8 caracteres.",
        }), 400

    if confirmacao is not None and nova_senha != confirmacao:
        return jsonify({
            "sucesso": False,
            "erro": "A confirmação de senha não confere.",
        }), 400

    usuario = Usuario.query.filter_by(token_recuperacao=token).first()

    if not usuario or not usuario.validar_token_recuperacao(token):
        registrar_seguranca(
            evento="TOKEN_RECUPERACAO_INVALIDO",
            ip=ip,
            detalhes=f"Tentativa de uso de token inválido ou expirado: {token[:10]}...",
        )
        return jsonify({
            "sucesso": False,
            "erro": "Token de recuperação inválido ou expirado. Por favor, solicite um novo link de recuperação.",
        }), 400

    try:
        usuario.definir_senha(nova_senha)
        usuario.limpar_token_recuperacao()
        db.session.commit()

        registrar_seguranca(
            evento="REDEFINICAO_SENHA_SUCESSO",
            ip=ip,
            usuario_id=usuario.id,
            detalhes=f"Senha redefinida com sucesso para o usuário {usuario.email}",
        )

        return jsonify({
            "sucesso": True,
            "mensagem": "Sua senha foi redefinida com sucesso! Você já pode realizar login com a nova senha.",
        }), 200

    except Exception as e:
        db.session.rollback()
        tb = str(e)
        registrar_erro(
            nivel="ERROR",
            mensagem=f"Falha ao redefinir senha: {tb}",
            rota="POST /api/auth/redefinir-senha",
            stack_trace=tb,
            ip=ip,
        )
        return jsonify({
            "sucesso": False,
            "erro": "Ocorreu um erro ao redefinir sua senha. Por favor, tente novamente.",
        }), 500


# ==============================================================================
# Fluxo Google OAuth 2.0 (FSD Seções 6.1, 13.1.3 e 23)
# ==============================================================================

@auth_bp.route("/api/auth/google", methods=["GET"])
def api_google_login():
    """Inicia o fluxo de autorização OAuth 2.0 com o Google."""
    client_id = current_app.config.get("GOOGLE_CLIENT_ID")
    client_secret = current_app.config.get("GOOGLE_CLIENT_SECRET")

    # Verifica se as credenciais foram configuradas ou se permanecem de exemplo
    if not client_id or not client_secret or "seu-google-client-id" in client_id:
        return jsonify({
            "sucesso": False,
            "erro": "A integração com Google OAuth 2.0 requer credenciais válidas configuradas no config/config.py (GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET).",
        }), 501

    try:
        from requests_oauthlib import OAuth2Session

        redirect_uri = url_for("auth.api_google_callback", _external=True)
        escopos = [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ]
        google = OAuth2Session(client_id, scope=escopos, redirect_uri=redirect_uri)
        authorization_url, state = google.authorization_url(
            "https://accounts.google.com/o/oauth2/v2/auth",
            access_type="offline",
            prompt="select_account",
        )
        session["oauth_state"] = state
        return redirect(authorization_url)

    except Exception as e:
        tb = str(e)
        registrar_erro(
            nivel="ERROR",
            mensagem=f"Erro ao iniciar fluxo Google OAuth: {tb}",
            rota="GET /api/auth/google",
            stack_trace=tb,
            ip=obter_ip_cliente(),
        )
        return redirect(url_for("auth.login_view", erro="google_oauth_iniciacao_falha"))


@auth_bp.route("/api/auth/google/callback", methods=["GET"])
def api_google_callback():
    """Recebe o retorno do Google OAuth 2.0, provisiona usuário se novo e inicializa sessão (FSD 13.1.3)."""
    # 1. Tratamento de cancelamento pelo usuário ou erro do Google
    erro_google = request.args.get("error")
    if erro_google:
        registrar_seguranca(
            evento="GOOGLE_AUTH_CANCELADO",
            ip=obter_ip_cliente(),
            detalhes=f"Usuário cancelou ou ocorreu erro no consentimento Google: {erro_google}",
        )
        return redirect(url_for("auth.login_view", erro="google_auth_cancelado"))

    client_id = current_app.config.get("GOOGLE_CLIENT_ID")
    client_secret = current_app.config.get("GOOGLE_CLIENT_SECRET")
    redirect_uri = url_for("auth.api_google_callback", _external=True)

    try:
        from requests_oauthlib import OAuth2Session
        import requests

        state = session.get("oauth_state")
        google = OAuth2Session(client_id, state=state, redirect_uri=redirect_uri)

        token_url = "https://oauth2.googleapis.com/token"
        google.fetch_token(
            token_url,
            client_secret=client_secret,
            authorization_response=request.url,
        )

        # 2. Consulta de dados de perfil do usuário no Google
        user_info_resp = google.get("https://www.googleapis.com/oauth2/v3/userinfo")
        if user_info_resp.status_code != 200:
            raise RuntimeError(f"Erro ao obter userinfo do Google: HTTP {user_info_resp.status_code}")

        user_info = user_info_resp.json()
        google_id = user_info.get("sub")
        email = (user_info.get("email") or "").strip().lower()
        nome = user_info.get("name") or email.split("@")[0]

        if not email or not google_id:
            raise ValueError("Resposta do Google não forneceu e-mail ou identificador único válido.")

        # 3. Localização ou provisionamento atômico do usuário
        usuario = Usuario.query.filter(
            db.or_(Usuario.google_id == google_id, Usuario.email == email)
        ).first()

        if not usuario:
            # Primeiro acesso via Google: provisionamento atômico
            usuario = Usuario(
                nome=nome,
                email=email,
                google_id=google_id,
                tema_preferido="dark",
            )
            db.session.add(usuario)
            db.session.flush()

            provisionar_dados_iniciais_usuario(usuario)
            db.session.commit()

            registrar_seguranca(
                evento="CADASTRO_GOOGLE_SUCESSO",
                ip=obter_ip_cliente(),
                usuario_id=usuario.id,
                detalhes=f"Novo usuário cadastrado automaticamente via Google OAuth: {email}",
            )
        else:
            # Se já existia por e-mail mas ainda não tinha google_id associado
            if not usuario.google_id:
                usuario.google_id = google_id
                db.session.commit()

            registrar_seguranca(
                evento="LOGIN_GOOGLE_SUCESSO",
                ip=obter_ip_cliente(),
                usuario_id=usuario.id,
                detalhes=f"Login efetuado via Google OAuth para {email}",
            )

        # 4. Inicialização de sessão segura
        session.clear()
        session["usuario_id"] = usuario.id
        session.permanent = True

        return redirect(url_for("auth.dashboard_view"))

    except Exception as e:
        db.session.rollback()
        tb = str(e)
        registrar_erro(
            nivel="ERROR",
            mensagem=f"Falha no callback do Google OAuth: {tb}",
            rota="GET /api/auth/google/callback",
            stack_trace=tb,
            ip=obter_ip_cliente(),
        )
        return redirect(url_for("auth.login_view", erro="google_auth_falha"))

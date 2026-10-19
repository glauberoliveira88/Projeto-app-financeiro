"""Controller de Configurações, Perfil e Preferências do FinançasSimples.

Conforme docs/FSD.md (Seções 6.1, 11.1, 12.9 e 13.8) e docs/DESIGN.md:
- Consulta de dados cadastrais do perfil do usuário autenticado (GET /api/usuario/perfil);
- Atualização cadastral básica de nome com sanitização (PUT /api/usuario/perfil);
- Persistência da preferência de tema visual dark/light (PATCH /api/usuario/tema);
- Rigoroso isolamento por usuario_id (anti-IDOR) via current_user.
"""
import html
from flask import Blueprint, jsonify, request
from app.models import db
from app.models.usuario import Usuario
from app.utils.auth import current_user, login_required
from app.services.logger_service import registrar_erro

configuracoes_bp = Blueprint("configuracoes", __name__, url_prefix="/api/usuario")


@configuracoes_bp.route("/perfil", methods=["GET"])
@login_required
def obter_perfil():
    """Retorna os dados cadastrais do usuário autenticado na sessão.

    docs/FSD.md - Seções 12.9 e 15.
    """
    try:
        usuario = db.session.get(Usuario, current_user.id)
        if not usuario:
            return jsonify({
                "sucesso": False,
                "erro": "Usuário não encontrado.",
            }), 404

        return jsonify({
            "sucesso": True,
            "dados": usuario.to_dict(),
        }), 200
    except Exception as e:
        registrar_erro(
            nivel="ERROR",
            rota="GET /api/usuario/perfil",
            mensagem=f"Erro ao obter perfil do usuário: {str(e)}",
            usuario_id=getattr(current_user, "id", None),
        )
        return jsonify({
            "sucesso": False,
            "erro": "Ocorreu um erro interno ao carregar os dados do seu perfil.",
        }), 500


@configuracoes_bp.route("/perfil", methods=["PUT", "PATCH"])
@login_required
def atualizar_perfil():
    """Atualiza informações cadastrais básicas do usuário (ex: nome completo).

    docs/FSD.md - Seções 12.9 e 14.1.
    """
    try:
        dados = request.get_json(silent=True) or {}
        novo_nome = dados.get("nome")

        if novo_nome is None:
            return jsonify({
                "sucesso": False,
                "erro": "O campo 'nome' é obrigatório.",
            }), 400

        novo_nome = str(novo_nome).strip()

        # Validação de regras de negócio (docs/FSD.md - Seção 14.1: tamanho entre 2 e 150 caracteres)
        if len(novo_nome) < 2:
            return jsonify({
                "sucesso": False,
                "erro": "O nome deve conter no mínimo 2 caracteres.",
            }), 400

        if len(novo_nome) > 150:
            return jsonify({
                "sucesso": False,
                "erro": "O nome não pode exceder 150 caracteres.",
            }), 400

        # Sanitização contra tags HTML / XSS armazenado
        nome_sanitizado = html.escape(novo_nome)

        usuario = db.session.get(Usuario, current_user.id)
        if not usuario:
            return jsonify({
                "sucesso": False,
                "erro": "Usuário não encontrado.",
            }), 404

        usuario.nome = nome_sanitizado
        db.session.commit()

        return jsonify({
            "sucesso": True,
            "mensagem": "Perfil atualizado com sucesso.",
            "dados": usuario.to_dict(),
            "usuario": usuario.to_dict(),
        }), 200
    except Exception as e:
        db.session.rollback()
        registrar_erro(
            nivel="ERROR",
            rota="PUT /api/usuario/perfil",
            mensagem=f"Erro ao atualizar perfil do usuário: {str(e)}",
            usuario_id=getattr(current_user, "id", None),
        )
        return jsonify({
            "sucesso": False,
            "erro": "Não foi possível salvar as alterações do perfil. Tente novamente.",
        }), 500


@configuracoes_bp.route("/tema", methods=["PATCH"])
@login_required
def atualizar_tema():
    """Persiste a preferência visual de tema (dark ou light) do usuário.

    docs/FSD.md - Seções 12.9 e 13.8.
    """
    try:
        dados = request.get_json(silent=True) or {}
        novo_tema = dados.get("tema")

        if not novo_tema or str(novo_tema).lower() not in ("dark", "light"):
            return jsonify({
                "sucesso": False,
                "erro": "Tema inválido. O valor deve ser 'dark' ou 'light'.",
            }), 400

        tema_normalizado = str(novo_tema).lower()

        usuario = db.session.get(Usuario, current_user.id)
        if not usuario:
            return jsonify({
                "sucesso": False,
                "erro": "Usuário não encontrado.",
            }), 404

        usuario.tema_preferido = tema_normalizado
        db.session.commit()

        return jsonify({
            "sucesso": True,
            "mensagem": "Tema preferido salvo com sucesso.",
            "dados": {
                "tema_preferido": usuario.tema_preferido,
            },
        }), 200
    except Exception as e:
        db.session.rollback()
        registrar_erro(
            nivel="ERROR",
            rota="PATCH /api/usuario/tema",
            mensagem=f"Erro ao persistir preferência de tema do usuário: {str(e)}",
            usuario_id=getattr(current_user, "id", None),
        )
        return jsonify({
            "sucesso": False,
            "erro": "Ocorreu um erro ao salvar sua preferência de tema.",
        }), 500

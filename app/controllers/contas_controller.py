"""Controller de Contas e Carteiras do FinançasSimples (docs/FSD.md - Seções 6.5, 12.6).

Implementa os endpoints da API REST para gestão completa de contas/carteiras:
- Listagem com saldo em tempo real (fórmula contábil).
- Criação com validação de unicidade de nome por usuário.
- Edição do nome da conta.
- Arquivamento e reativação lógica.
- Exclusão física bloqueada se houver movimentações vinculadas.

Todos os endpoints exigem autenticação e isolam dados por usuario_id.
"""
from flask import Blueprint, jsonify, request
from app.models import db
from app.models.conta import Conta
from app.models.lancamento import Lancamento
from app.models.lancamento_recorrente import LancamentoRecorrente
from app.utils.auth import current_user, login_required, validar_posse

contas_bp = Blueprint("contas", __name__, url_prefix="/api/contas")


@contas_bp.route("", methods=["GET"])
@login_required
def listar_contas():
    """Lista todas as contas do usuário logado com saldo em tempo real.

    Retorna contas ativas e arquivadas, separadas no payload para facilitar
    a renderização de seções distintas na interface.
    """
    usuario_id = current_user.id

    contas = (
        Conta.query
        .filter_by(usuario_id=usuario_id)
        .order_by(Conta.status.asc(), Conta.nome.asc())
        .all()
    )

    lista = [c.to_dict(incluir_saldo=True) for c in contas]

    # Saldo consolidado de todas as contas ativas
    saldo_total = sum(
        c["saldo_atual"] for c in lista if c["status"] == "ativo" and c["saldo_atual"] is not None
    )

    return jsonify({
        "sucesso": True,
        "dados": {
            "contas": lista,
            "saldo_total_ativo": round(saldo_total, 2),
        },
    }), 200


@contas_bp.route("", methods=["POST"])
@login_required
def criar_conta():
    """Cria uma nova conta/carteira para o usuário autenticado.

    Corpo esperado (JSON):
        nome (str): Nome único da conta para o usuário. Obrigatório.
        saldo_inicial (float): Saldo de abertura da conta. Padrão: 0.00.
    """
    usuario_id = current_user.id
    dados = request.get_json(silent=True) or {}

    nome = (dados.get("nome") or "").strip()
    if not nome:
        return jsonify({"sucesso": False, "erro": "O nome da conta é obrigatório."}), 400

    if len(nome) > 100:
        return jsonify({"sucesso": False, "erro": "O nome da conta não pode exceder 100 caracteres."}), 400

    # Validação de saldo inicial
    try:
        saldo_inicial = float(dados.get("saldo_inicial", 0.00))
    except (TypeError, ValueError):
        return jsonify({"sucesso": False, "erro": "O saldo inicial deve ser um valor numérico."}), 400

    # Verifica unicidade do nome para o usuário
    existe = Conta.query.filter_by(usuario_id=usuario_id, nome=nome).first()
    if existe:
        return jsonify({
            "sucesso": False,
            "erro": f'Você já possui uma conta com o nome "{nome}". Escolha um nome diferente.',
        }), 400

    nova_conta = Conta(
        usuario_id=usuario_id,
        nome=nome,
        saldo_inicial=saldo_inicial,
        status="ativo",
    )

    try:
        db.session.add(nova_conta)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"sucesso": False, "erro": "Não foi possível criar a conta. Tente novamente."}), 500

    return jsonify({
        "sucesso": True,
        "mensagem": f'Conta "{nome}" criada com sucesso.',
        "dados": {"conta": nova_conta.to_dict()},
    }), 201


@contas_bp.route("/<int:conta_id>", methods=["PUT"])
@login_required
def editar_conta(conta_id):
    """Edita o nome de uma conta existente do usuário.

    Corpo esperado (JSON):
        nome (str): Novo nome da conta. Obrigatório.
    """
    conta = db.session.get(Conta, conta_id)

    # Verifica existência e posse (defesa anti-IDOR)
    if not conta or not validar_posse(conta, "conta"):
        return jsonify({"sucesso": False, "erro": "Conta não encontrada ou acesso negado."}), 404

    dados = request.get_json(silent=True) or {}
    nome = (dados.get("nome") or "").strip()

    if not nome:
        return jsonify({"sucesso": False, "erro": "O novo nome da conta é obrigatório."}), 400

    if len(nome) > 100:
        return jsonify({"sucesso": False, "erro": "O nome não pode exceder 100 caracteres."}), 400

    # Verifica unicidade do novo nome (excluindo a própria conta)
    duplicado = (
        Conta.query
        .filter(
            Conta.usuario_id == current_user.id,
            Conta.nome == nome,
            Conta.id != conta_id,
        )
        .first()
    )
    if duplicado:
        return jsonify({
            "sucesso": False,
            "erro": f'Você já possui outra conta com o nome "{nome}".',
        }), 400

    nome_anterior = conta.nome
    conta.nome = nome

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"sucesso": False, "erro": "Erro ao salvar alteração. Tente novamente."}), 500

    return jsonify({
        "sucesso": True,
        "mensagem": f'Conta renomeada de "{nome_anterior}" para "{nome}" com sucesso.',
        "dados": {"conta": conta.to_dict()},
    }), 200


@contas_bp.route("/<int:conta_id>/arquivar", methods=["PATCH"])
@login_required
def arquivar_conta(conta_id):
    """Arquiva uma conta ativa, retirando-a dos seletores de novos lançamentos.

    Contas arquivadas mantêm todo o histórico intacto e podem ser reativadas.
    """
    conta = db.session.get(Conta, conta_id)

    if not conta or not validar_posse(conta, "conta"):
        return jsonify({"sucesso": False, "erro": "Conta não encontrada ou acesso negado."}), 404

    if conta.status == "arquivado":
        return jsonify({"sucesso": False, "erro": "Esta conta já está arquivada."}), 400

    conta.arquivar()

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"sucesso": False, "erro": "Erro ao arquivar conta. Tente novamente."}), 500

    return jsonify({
        "sucesso": True,
        "mensagem": f'Conta "{conta.nome}" arquivada com sucesso.',
        "dados": {"conta": conta.to_dict()},
    }), 200


@contas_bp.route("/<int:conta_id>/reativar", methods=["PATCH"])
@login_required
def reativar_conta(conta_id):
    """Reativa uma conta previamente arquivada, tornando-a disponível novamente."""
    conta = db.session.get(Conta, conta_id)

    if not conta or not validar_posse(conta, "conta"):
        return jsonify({"sucesso": False, "erro": "Conta não encontrada ou acesso negado."}), 404

    if conta.status == "ativo":
        return jsonify({"sucesso": False, "erro": "Esta conta já está ativa."}), 400

    conta.reativar()

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"sucesso": False, "erro": "Erro ao reativar conta. Tente novamente."}), 500

    return jsonify({
        "sucesso": True,
        "mensagem": f'Conta "{conta.nome}" reativada com sucesso.',
        "dados": {"conta": conta.to_dict()},
    }), 200


@contas_bp.route("/<int:conta_id>", methods=["DELETE"])
@login_required
def excluir_conta(conta_id):
    """Exclui uma conta/carteira do usuário autenticado.

    Se a conta possuir movimentações vinculadas (lançamentos ou fixos recorrentes):
    - Se 'excluir_vinculados' for informado (via query param ou corpo JSON),
      exclui em transação atômica a conta e todas as informações vinculadas a ela.
    - Se não for informado, bloqueia a exclusão direta e retorna os vínculos existentes,
      oferecendo ao usuário a opção de exclusão conjunta ou arquivamento.
    """
    conta = db.session.get(Conta, conta_id)

    if not conta or not validar_posse(conta, "conta"):
        return jsonify({"sucesso": False, "erro": "Conta não encontrada ou acesso negado."}), 404

    # Parâmetro para exclusão em lote com vínculos (suporta query string ou JSON body)
    dados = request.get_json(silent=True) or {}
    excluir_vinculados_param = request.args.get("excluir_vinculados", "").lower() in ("true", "1", "sim")
    excluir_vinculados_body = bool(dados.get("excluir_vinculados"))
    excluir_vinculados = excluir_vinculados_param or excluir_vinculados_body

    tem_mov = conta.tem_movimentacoes()

    if tem_mov and not excluir_vinculados:
        total_lancamentos = (
            Lancamento.query
            .filter(
                Lancamento.usuario_id == current_user.id,
                db.or_(
                    Lancamento.conta_id == conta.id,
                    Lancamento.conta_destino_id == conta.id,
                ),
            )
            .count()
        )
        total_recorrentes = (
            LancamentoRecorrente.query
            .filter_by(usuario_id=current_user.id, conta_id=conta.id)
            .count()
        )

        return jsonify({
            "sucesso": False,
            "erro": (
                f'A conta "{conta.nome}" possui movimentações registradas no histórico e não pode ser excluída diretamente.'
            ),
            "tem_vinculos": True,
            "total_lancamentos": total_lancamentos,
            "total_recorrentes": total_recorrentes,
            "acao_sugerida": "excluir_vinculados_ou_arquivar",
        }), 400

    nome_conta = conta.nome

    try:
        total_lanc_excluidos = 0
        total_rec_excluidos = 0

        if tem_mov and excluir_vinculados:
            # 1. Exclui todos os lançamentos vinculados (origem ou destino) do usuário
            total_lanc_excluidos = (
                Lancamento.query
                .filter(
                    Lancamento.usuario_id == current_user.id,
                    db.or_(
                        Lancamento.conta_id == conta.id,
                        Lancamento.conta_destino_id == conta.id,
                    ),
                )
                .delete(synchronize_session=False)
            )

            # 2. Exclui todos os modelos recorrentes vinculados à conta
            total_rec_excluidos = (
                LancamentoRecorrente.query
                .filter_by(usuario_id=current_user.id, conta_id=conta.id)
                .delete(synchronize_session=False)
            )

        db.session.delete(conta)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"sucesso": False, "erro": "Erro ao excluir conta. Tente novamente."}), 500

    mensagem = (
        f'Conta "{nome_conta}" e todas as informações vinculadas foram excluídas permanentemente.'
        if tem_mov and excluir_vinculados
        else f'Conta "{nome_conta}" excluída permanentemente.'
    )

    return jsonify({
        "sucesso": True,
        "mensagem": mensagem,
        "dados": {
            "total_lancamentos_excluidos": total_lanc_excluidos,
            "total_recorrentes_excluidos": total_rec_excluidos,
        },
    }), 200


@contas_bp.route("/<int:conta_id>/excluir-com-vinculos", methods=["POST"])
@login_required
def excluir_conta_com_vinculos(conta_id):
    """Endpoint alternativo POST para excluir a conta e todas as informações vinculadas em lote."""
    conta = db.session.get(Conta, conta_id)

    if not conta or not validar_posse(conta, "conta"):
        return jsonify({"sucesso": False, "erro": "Conta não encontrada ou acesso negado."}), 404

    nome_conta = conta.nome

    try:
        # 1. Exclui todos os lançamentos vinculados (origem ou destino) do usuário
        total_lancamentos = (
            Lancamento.query
            .filter(
                Lancamento.usuario_id == current_user.id,
                db.or_(
                    Lancamento.conta_id == conta.id,
                    Lancamento.conta_destino_id == conta.id,
                ),
            )
            .delete(synchronize_session=False)
        )

        # 2. Exclui todos os modelos recorrentes vinculados à conta
        total_recorrentes = (
            LancamentoRecorrente.query
            .filter_by(usuario_id=current_user.id, conta_id=conta.id)
            .delete(synchronize_session=False)
        )

        # 3. Exclui a conta
        db.session.delete(conta)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"sucesso": False, "erro": "Erro ao excluir conta e vínculos. Tente novamente."}), 500

    return jsonify({
        "sucesso": True,
        "mensagem": f'Conta "{nome_conta}" e todas as suas informações vinculadas foram excluídas com sucesso.',
        "dados": {
            "total_lancamentos_excluidos": total_lancamentos,
            "total_recorrentes_excluidos": total_recorrentes,
        },
    }), 200

"""Controller de Lançamentos do FinançasSimples (docs/FSD.md - Seções 6.3, 12.4, 12.5 e 13.2).

Implementa os endpoints da API REST para gestão completa de movimentações financeiras:
- Listagem filtrada por período (mês/ano), conta, categoria, tipo, status e busca textual.
- Registro de novas receitas e despesas.
- Transferências entre contas próprias (sem inflar receitas/despesas gerais).
- Edição de lançamentos existentes.
- Alternância rápida de status (pago <-> pendente).
- Exclusão lógica (soft delete) com deleted_at e recálculo dinâmico de saldos.

Todos os endpoints exigem autenticação (@login_required) e isolam dados por usuario_id.
"""
from datetime import datetime, date, timezone
from decimal import Decimal
from flask import Blueprint, jsonify, request
from sqlalchemy import extract, or_

from app.models import db
from app.models.lancamento import Lancamento, obter_data_hora_utc
from app.models.conta import Conta
from app.models.categoria import Categoria
from app.utils.auth import current_user, login_required, validar_posse

lancamentos_bp = Blueprint("lancamentos", __name__, url_prefix="/api/lancamentos")


def converter_data(data_str: str) -> date:
    """Converte string no formato YYYY-MM-DD para objeto date."""
    if not data_str:
        return None
    try:
        return datetime.strptime(data_str.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None


@lancamentos_bp.route("", methods=["GET"])
@login_required
def listar_lancamentos():
    """Lista lançamentos do usuário autenticado com suporte a múltiplos filtros.

    Parâmetros aceitos na query string:
        mes (int): Mês de competência (1 a 12).
        ano (int): Ano de competência (ex: 2026).
        conta_id (int): ID da conta (origem ou destino).
        categoria_id (int): ID da categoria.
        tipo (str): 'receita', 'despesa' ou 'transferencia'.
        status (str): 'pago' ou 'pendente'.
        busca (str): Termo de busca textual na descrição.
    """
    usuario_id = current_user.id

    # 1. Filtro por Ano e Mês de Competência
    mes = request.args.get("mes", type=int)
    ano = request.args.get("ano", type=int)

    # Sincronização automática transparente de lançamentos recorrentes (docs/FSD.md - Seção 6.4 e 13.4)
    try:
        from app.services.recorrentes_service import sincronizar_recorrencias_usuario
        hoje = date.today()
        ano_sinc = ano or hoje.year
        mes_sinc = mes or hoje.month
        sincronizar_recorrencias_usuario(usuario_id=usuario_id, ano=ano_sinc, mes=mes_sinc)
        if (ano_sinc, mes_sinc) != (hoje.year, hoje.month):
            sincronizar_recorrencias_usuario(usuario_id=usuario_id, ano=hoje.year, mes=hoje.month)
    except Exception:
        pass  # Falha silenciosa para não travar a listagem caso ocorra instabilidade temporária

    # Base query: lançamentos do usuário que não foram excluídos logicamente
    query = (
        Lancamento.query
        .filter(
            Lancamento.usuario_id == usuario_id,
            Lancamento.deleted_at.is_(None),
        )
    )
    if ano:
        query = query.filter(extract("year", Lancamento.data_competencia) == ano)
    if mes:
        query = query.filter(extract("month", Lancamento.data_competencia) == mes)

    # 2. Filtro por Conta
    conta_id = request.args.get("conta_id", type=int) or request.args.get("conta", type=int)
    if conta_id:
        query = query.filter(
            or_(
                Lancamento.conta_id == conta_id,
                Lancamento.conta_destino_id == conta_id,
            )
        )

    # 3. Filtro por Categoria
    categoria_id = request.args.get("categoria_id", type=int) or request.args.get("categoria", type=int)
    if categoria_id:
        query = query.filter(Lancamento.categoria_id == categoria_id)

    # 4. Filtro por Tipo de Movimentação
    tipo = request.args.get("tipo", type=str)
    if tipo and tipo in ("receita", "despesa", "transferencia"):
        query = query.filter(Lancamento.tipo == tipo)

    # 5. Filtro por Status
    status = request.args.get("status", type=str)
    if status and status in ("pago", "pendente"):
        query = query.filter(Lancamento.status == status)

    # 6. Busca textual na descrição
    busca = (request.args.get("busca") or "").strip()
    if busca:
        query = query.filter(Lancamento.descricao.ilike(f"%{busca}%"))

    # Ordenação decrescente por data de competência e ID
    lancamentos = (
        query
        .order_by(Lancamento.data_competencia.desc(), Lancamento.id.desc())
        .all()
    )

    lista = [l.to_dict() for l in lancamentos]

    # Consolidação rápida dos valores filtrados
    total_receitas = sum(l["valor"] for l in lista if l["tipo"] == "receita")
    total_despesas = sum(l["valor"] for l in lista if l["tipo"] == "despesa")
    total_transferencias = sum(l["valor"] for l in lista if l["tipo"] == "transferencia")
    saldo_periodo = total_receitas - total_despesas
    total_pendentes = len([l for l in lista if l["status"] == "pendente"])
    total_vencidos = len([l for l in lista if l.get("vencido")])

    return jsonify({
        "sucesso": True,
        "dados": {
            "lancamentos": lista,
            "resumo": {
                "total_receitas": round(total_receitas, 2),
                "total_despesas": round(total_despesas, 2),
                "total_transferencias": round(total_transferencias, 2),
                "saldo_periodo": round(saldo_periodo, 2),
                "total_itens": len(lista),
                "total_pendentes": total_pendentes,
                "total_vencidos": total_vencidos,
            },
        },
    }), 200


@lancamentos_bp.route("", methods=["POST"])
@login_required
def criar_lancamento():
    """Registra um novo lançamento avulso de receita ou despesa.

    Corpo esperado (JSON):
        tipo (str): 'receita' ou 'despesa'. Obrigatório.
        valor (float): Valor monetário estritamente positivo (> 0.00). Obrigatório.
        data_competencia (str): Data no formato YYYY-MM-DD. Obrigatório.
        data_vencimento (str): Data no formato YYYY-MM-DD. Opcional (assume competência).
        descricao (str): Descrição legível da movimentação. Obrigatório.
        categoria_id (int): ID da categoria correspondente. Obrigatório.
        conta_id (int): ID da conta/carteira de origem. Obrigatório.
        forma_pagamento (str): Ex: 'Dinheiro', 'PIX', 'Cartão de Débito', etc.
        status (str): 'pago' ou 'pendente'. Padrão: 'pago'.
        observacao (str): Observações adicionais opcionais.
    """
    usuario_id = current_user.id
    dados = request.get_json(silent=True) or {}

    tipo = (dados.get("tipo") or "").strip().lower()
    if tipo not in ("receita", "despesa"):
        return jsonify({
            "sucesso": False,
            "erro": "O tipo do lançamento deve ser 'receita' ou 'despesa'. Para transferências, utilize a rota específica.",
        }), 400

    # Validação do valor monetário
    try:
        valor_raw = Decimal(str(dados.get("valor", 0)))
        if valor_raw <= Decimal("0.00"):
            return jsonify({"sucesso": False, "erro": "O valor do lançamento deve ser maior que zero."}), 400
        valor = valor_raw
    except Exception:
        return jsonify({"sucesso": False, "erro": "Valor numérico inválido."}), 400

    # Validação da descrição
    descricao = (dados.get("descricao") or "").strip()
    if not descricao:
        return jsonify({"sucesso": False, "erro": "A descrição do lançamento é obrigatória."}), 400
    if len(descricao) > 200:
        return jsonify({"sucesso": False, "erro": "A descrição não pode exceder 200 caracteres."}), 400

    # Validação das datas
    data_comp = converter_data(dados.get("data_competencia"))
    if not data_comp:
        return jsonify({"sucesso": False, "erro": "Data de competência inválida. Utilize o formato AAAA-MM-DD."}), 400

    data_venc = converter_data(dados.get("data_vencimento")) or data_comp

    # Validação da conta (posse e status)
    conta_id = dados.get("conta_id")
    if not conta_id:
        return jsonify({"sucesso": False, "erro": "A conta/carteira é obrigatória."}), 400

    conta = db.session.get(Conta, conta_id)
    if not conta or conta.usuario_id != usuario_id:
        return jsonify({"sucesso": False, "erro": "Conta não encontrada ou acesso negado."}), 403

    if conta.status == "arquivado":
        return jsonify({
            "sucesso": False,
            "erro": f'A conta "{conta.nome}" está arquivada e não aceita novos lançamentos. Reative-a ou selecione outra conta.',
        }), 400

    # Validação da categoria (posse, compatibilidade de tipo e status)
    categoria_id = dados.get("categoria_id")
    if not categoria_id:
        return jsonify({"sucesso": False, "erro": "A categoria é obrigatória."}), 400

    categoria = db.session.get(Categoria, categoria_id)
    if not categoria or categoria.usuario_id != usuario_id:
        return jsonify({"sucesso": False, "erro": "Categoria não encontrada ou acesso negado."}), 403

    if categoria.tipo != tipo:
        return jsonify({
            "sucesso": False,
            "erro": f'A categoria "{categoria.nome}" é de {categoria.tipo} e não pode ser associada a um lançamento de {tipo}.',
        }), 400

    if categoria.status == "arquivado":
        return jsonify({
            "sucesso": False,
            "erro": f'A categoria "{categoria.nome}" está arquivada. Reative-a ou selecione outra categoria.',
        }), 400

    # Status de liquidação
    status = (dados.get("status") or "pago").strip().lower()
    if status not in ("pago", "pendente"):
        status = "pago"

    forma_pagamento = (dados.get("forma_pagamento") or "Dinheiro").strip()
    if len(forma_pagamento) > 50:
        forma_pagamento = forma_pagamento[:50]

    observacao = (dados.get("observacao") or "").strip() or None

    novo_lancamento = Lancamento(
        usuario_id=usuario_id,
        tipo=tipo,
        valor=valor,
        data_competencia=data_comp,
        data_vencimento=data_venc,
        descricao=descricao,
        categoria_id=categoria.id,
        conta_id=conta.id,
        conta_destino_id=None,
        forma_pagamento=forma_pagamento,
        status=status,
        observacao=observacao,
    )

    try:
        db.session.add(novo_lancamento)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"sucesso": False, "erro": "Não foi possível registrar o lançamento. Tente novamente."}), 500

    return jsonify({
        "sucesso": True,
        "mensagem": f'Lançamento "{descricao}" registrado com sucesso.',
        "dados": {"lancamento": novo_lancamento.to_dict()},
    }), 201


@lancamentos_bp.route("/transferencia", methods=["POST"])
@login_required
def criar_transferencia():
    """Registra uma transferência entre duas contas próprias do usuário.

    Regras de negócio do FSD (Seções 6.3, 13.3 e 14.2):
    - Debita a conta de origem e credita a conta de destino.
    - Contas de origem e destino devem ser diferentes e pertencer ao usuário.
    - categoria_id é NULL.
    - data_vencimento é automaticamente idêntica a data_competencia.
    - status é sempre 'pago'.
    - Transferências não alteram os somatórios de receitas ou despesas gerais.
    - Alerta preventivo se o valor da transferência for maior que o saldo da conta de origem,
      permitindo confirmação explícita via flag 'confirmar_saldo_negativo'.
    """
    usuario_id = current_user.id
    dados = request.get_json(silent=True) or {}

    # Validação do valor
    try:
        valor_raw = Decimal(str(dados.get("valor", 0)))
        if valor_raw <= Decimal("0.00"):
            return jsonify({"sucesso": False, "erro": "O valor da transferência deve ser maior que zero."}), 400
        valor = valor_raw
    except Exception:
        return jsonify({"sucesso": False, "erro": "Valor numérico inválido."}), 400

    conta_origem_id = dados.get("conta_id") or dados.get("conta_origem_id")
    conta_destino_id = dados.get("conta_destino_id")

    if not conta_origem_id or not conta_destino_id:
        return jsonify({
            "sucesso": False,
            "erro": "As contas de origem e destino são obrigatórias.",
        }), 400

    if int(conta_origem_id) == int(conta_destino_id):
        return jsonify({
            "sucesso": False,
            "erro": "A conta de destino deve ser diferente da conta de origem.",
        }), 400

    # Validação e posse da conta de origem
    conta_origem = db.session.get(Conta, conta_origem_id)
    if not conta_origem or conta_origem.usuario_id != usuario_id:
        return jsonify({"sucesso": False, "erro": "Conta de origem não encontrada ou acesso negado."}), 403

    if conta_origem.status == "arquivado":
        return jsonify({
            "sucesso": False,
            "erro": f'A conta de origem "{conta_origem.nome}" está arquivada.',
        }), 400

    # Validação e posse da conta de destino
    conta_destino = db.session.get(Conta, conta_destino_id)
    if not conta_destino or conta_destino.usuario_id != usuario_id:
        return jsonify({"sucesso": False, "erro": "Conta de destino não encontrada ou acesso negado."}), 403

    if conta_destino.status == "arquivado":
        return jsonify({
            "sucesso": False,
            "erro": f'A conta de destino "{conta_destino.nome}" está arquivada.',
        }), 400

    # Alerta preventivo de saldo insuficiente na conta de origem (FSD 14.2 item 6)
    saldo_atual_origem = conta_origem.calcular_saldo_atual()
    confirmar_saldo_negativo = bool(dados.get("confirmar_saldo_negativo", False))
    if valor > saldo_atual_origem and not confirmar_saldo_negativo:
        return jsonify({
            "sucesso": False,
            "requer_confirmacao": True,
            "saldo_atual_origem": float(saldo_atual_origem),
            "erro": (
                f'O valor da transferência (R$ {valor:,.2f}) é maior que o saldo atual da conta "{conta_origem.nome}" '
                f"(R$ {saldo_atual_origem:,.2f}). Deseja continuar mesmo assim?"
            ),
        }), 409

    data_transf = converter_data(dados.get("data_competencia") or dados.get("data"))
    if not data_transf:
        data_transf = date.today()

    descricao = (dados.get("descricao") or "").strip()
    if not descricao:
        descricao = f"Transferência: {conta_origem.nome} → {conta_destino.nome}"

    observacao = (dados.get("observacao") or "").strip() or None
    forma_pagamento = (dados.get("forma_pagamento") or "Transferência").strip()

    nova_transferencia = Lancamento(
        usuario_id=usuario_id,
        tipo="transferencia",
        valor=valor,
        data_competencia=data_transf,
        data_vencimento=data_transf,  # idêntica à competência em transferências
        descricao=descricao,
        categoria_id=None,  # nulo em transferências
        conta_id=conta_origem.id,
        conta_destino_id=conta_destino.id,
        forma_pagamento=forma_pagamento,
        status="pago",  # transferências são registradas como pago
        observacao=observacao,
    )

    try:
        db.session.add(nova_transferencia)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"sucesso": False, "erro": "Erro ao registrar transferência. Tente novamente."}), 500

    return jsonify({
        "sucesso": True,
        "mensagem": f'Transferência de R$ {valor:,.2f} realizada com sucesso.',
        "dados": {
            "lancamento": nova_transferencia.to_dict(),
            "saldo_origem_atualizado": float(conta_origem.calcular_saldo_atual()),
            "saldo_destino_atualizado": float(conta_destino.calcular_saldo_atual()),
        },
    }), 201


@lancamentos_bp.route("/<int:lancamento_id>", methods=["PUT"])
@login_required
def editar_lancamento(lancamento_id):
    """Edita um lançamento existente (receita, despesa ou transferência)."""
    usuario_id = current_user.id
    lancamento = db.session.get(Lancamento, lancamento_id)

    # Validação de existência e posse anti-IDOR
    if not lancamento or not validar_posse(lancamento, "lançamento"):
        return jsonify({"sucesso": False, "erro": "Lançamento não encontrado ou acesso negado."}), 404

    if lancamento.esta_excluido:
        return jsonify({"sucesso": False, "erro": "Não é possível editar um lançamento excluído."}), 400

    dados = request.get_json(silent=True) or {}

    # Se for transferência
    if lancamento.tipo == "transferencia":
        try:
            valor_raw = Decimal(str(dados.get("valor", lancamento.valor)))
            if valor_raw <= Decimal("0.00"):
                return jsonify({"sucesso": False, "erro": "O valor deve ser maior que zero."}), 400
            lancamento.valor = valor_raw
        except Exception:
            return jsonify({"sucesso": False, "erro": "Valor inválido."}), 400

        data_transf = converter_data(dados.get("data_competencia") or dados.get("data"))
        if data_transf:
            lancamento.data_competencia = data_transf
            lancamento.data_vencimento = data_transf

        if "descricao" in dados and dados["descricao"]:
            lancamento.descricao = dados["descricao"].strip()[:200]

        if "observacao" in dados:
            lancamento.observacao = dados["observacao"].strip() or None

        # Permite alterar contas se fornecidas
        origem_id = dados.get("conta_id")
        destino_id = dados.get("conta_destino_id")
        if origem_id and destino_id:
            if int(origem_id) == int(destino_id):
                return jsonify({"sucesso": False, "erro": "A conta de destino deve ser diferente da conta de origem."}), 400
            conta_o = db.session.get(Conta, origem_id)
            conta_d = db.session.get(Conta, destino_id)
            if not conta_o or conta_o.usuario_id != usuario_id or not conta_d or conta_d.usuario_id != usuario_id:
                return jsonify({"sucesso": False, "erro": "Contas inválidas ou acesso negado."}), 403
            lancamento.conta_id = conta_o.id
            lancamento.conta_destino_id = conta_d.id

        try:
            db.session.commit()
            return jsonify({
                "sucesso": True,
                "mensagem": "Transferência atualizada com sucesso.",
                "dados": {"lancamento": lancamento.to_dict()},
            }), 200
        except Exception:
            db.session.rollback()
            return jsonify({"sucesso": False, "erro": "Erro ao atualizar transferência."}), 500

    # Lançamento comum (receita ou despesa)
    try:
        valor_raw = Decimal(str(dados.get("valor", lancamento.valor)))
        if valor_raw <= Decimal("0.00"):
            return jsonify({"sucesso": False, "erro": "O valor deve ser maior que zero."}), 400
        lancamento.valor = valor_raw
    except Exception:
        return jsonify({"sucesso": False, "erro": "Valor inválido."}), 400

    descricao = (dados.get("descricao") or "").strip()
    if descricao:
        lancamento.descricao = descricao[:200]

    data_comp = converter_data(dados.get("data_competencia"))
    if data_comp:
        lancamento.data_competencia = data_comp

    data_venc = converter_data(dados.get("data_vencimento"))
    if data_venc:
        lancamento.data_vencimento = data_venc

    # Validação de Conta
    if "conta_id" in dados:
        conta = db.session.get(Conta, dados["conta_id"])
        if not conta or conta.usuario_id != usuario_id:
            return jsonify({"sucesso": False, "erro": "Conta não encontrada ou acesso negado."}), 403
        lancamento.conta_id = conta.id

    # Validação de Categoria
    if "categoria_id" in dados:
        categoria = db.session.get(Categoria, dados["categoria_id"])
        if not categoria or categoria.usuario_id != usuario_id:
            return jsonify({"sucesso": False, "erro": "Categoria não encontrada ou acesso negado."}), 403
        if categoria.tipo != lancamento.tipo:
            return jsonify({
                "sucesso": False,
                "erro": f'A categoria "{categoria.nome}" é de {categoria.tipo} e não pode ser usada em {lancamento.tipo}.',
            }), 400
        lancamento.categoria_id = categoria.id

    if "forma_pagamento" in dados:
        lancamento.forma_pagamento = (dados["forma_pagamento"] or "Dinheiro").strip()[:50]

    if "status" in dados:
        novo_status = dados["status"].strip().lower()
        if novo_status in ("pago", "pendente"):
            lancamento.status = novo_status

    if "observacao" in dados:
        lancamento.observacao = (dados["observacao"] or "").strip() or None

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"sucesso": False, "erro": "Erro ao atualizar lançamento."}), 500

    return jsonify({
        "sucesso": True,
        "mensagem": "Lançamento atualizado com sucesso.",
        "dados": {"lancamento": lancamento.to_dict()},
    }), 200


@lancamentos_bp.route("/<int:lancamento_id>/pagar", methods=["PATCH"])
@login_required
def alternar_status_pagamento(lancamento_id):
    """Alterna rapidamente o status de liquidação do lançamento entre 'pago' e 'pendente'."""
    lancamento = db.session.get(Lancamento, lancamento_id)

    if not lancamento or not validar_posse(lancamento, "lançamento"):
        return jsonify({"sucesso": False, "erro": "Lançamento não encontrado ou acesso negado."}), 404

    if lancamento.esta_excluido:
        return jsonify({"sucesso": False, "erro": "Lançamento excluído não pode ter status alterado."}), 400

    novo_status = "pago" if lancamento.status == "pendente" else "pendente"
    lancamento.status = novo_status

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"sucesso": False, "erro": "Erro ao alternar status do lançamento."}), 500

    mensagem = "Lançamento marcado como pago." if novo_status == "pago" else "Lançamento reaberto como pendente."
    return jsonify({
        "sucesso": True,
        "mensagem": mensagem,
        "dados": {
            "lancamento": lancamento.to_dict(),
            "novo_status": novo_status,
        },
    }), 200


@lancamentos_bp.route("/<int:lancamento_id>", methods=["DELETE"])
@login_required
def excluir_lancamento(lancamento_id):
    """Executa exclusão lógica (soft delete) do lançamento.

    Preenche a coluna deleted_at com a data/hora atual em UTC.
    O saldo da conta envolvida é recalculado dinamicamente no próximo cálculo,
    pois as fórmulas de saldo desconsideram registros com deleted_at preenchido.
    """
    lancamento = db.session.get(Lancamento, lancamento_id)

    if not lancamento or not validar_posse(lancamento, "lançamento"):
        return jsonify({"sucesso": False, "erro": "Lançamento não encontrado ou acesso negado."}), 404

    if lancamento.esta_excluido:
        return jsonify({"sucesso": False, "erro": "Este lançamento já foi excluído."}), 400

    descricao = lancamento.descricao
    lancamento.soft_delete()

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"sucesso": False, "erro": "Erro ao excluir lançamento."}), 500

    return jsonify({
        "sucesso": True,
        "mensagem": f'Lançamento "{descricao}" excluído com sucesso.',
        "dados": {"id": lancamento_id},
    }), 200

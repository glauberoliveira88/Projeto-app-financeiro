"""Controller de Lançamentos Recorrentes do FinançasSimples (docs/FSD.md - Seções 6.4, 11.1, 12.8 e 13.4).

Implementa os endpoints da API REST sob o prefixo /api/recorrentes:
- GET /api/recorrentes: Listagem de modelos de fixos do usuário autenticado.
- POST /api/recorrentes: Cadastro de novo modelo com validações de conta, categoria e dia de vencimento (1 a 31).
- PUT /api/recorrentes/<id>: Edição de parâmetros do modelo existente.
- PATCH /api/recorrentes/<id>/toggle: Ativação ou desativação rápida do modelo.
- DELETE /api/recorrentes/<id>: Exclusão do modelo (sem remover histórico contábil de meses anteriores).
- POST /api/recorrentes/sincronizar: Gatilho manual para sincronização de fixos em mês/ano específico.

Todos os endpoints exigem autenticação (@login_required) e isolam dados por usuario_id (defesa anti-IDOR).
"""
from decimal import Decimal, InvalidOperation
from flask import Blueprint, jsonify, request

from app.models import db
from app.models.categoria import Categoria
from app.models.conta import Conta
from app.models.lancamento_recorrente import LancamentoRecorrente
from app.services.recorrentes_service import sincronizar_recorrencias_usuario
from app.utils.auth import current_user, login_required, validar_posse

recorrentes_bp = Blueprint("recorrentes", __name__, url_prefix="/api/recorrentes")


def converter_valor_decimal(valor_raw):
    """Converte valor monetário em Decimal de forma segura aceitando pt-BR e float/string."""
    if valor_raw is None or valor_raw == "":
        return None
    val_str = str(valor_raw).replace("R$", "").strip()
    if "," in val_str and "." in val_str:
        val_str = val_str.replace(".", "").replace(",", ".")
    elif "," in val_str:
        val_str = val_str.replace(",", ".")
    return Decimal(val_str)


@recorrentes_bp.route("", methods=["GET"])
@login_required
def listar_recorrentes():
    """Lista todos os modelos recorrentes pertencentes ao usuário autenticado."""
    usuario_id = current_user.id

    query = LancamentoRecorrente.query.filter_by(usuario_id=usuario_id)

    # Filtro opcional por tipo (receita / despesa)
    tipo = request.args.get("tipo", type=str)
    if tipo and tipo in ("receita", "despesa"):
        query = query.filter_by(tipo=tipo)

    # Filtro opcional por status ativo
    ativo = request.args.get("ativo")
    if ativo is not None:
        if ativo.lower() in ("true", "1"):
            query = query.filter_by(ativo=True)
        elif ativo.lower() in ("false", "0"):
            query = query.filter_by(ativo=False)

    # Ordena por dia de vencimento e depois por descrição
    modelos = query.order_by(LancamentoRecorrente.dia_vencimento.asc(), LancamentoRecorrente.descricao.asc()).all()

    return jsonify({
        "sucesso": True,
        "dados": {
            "recorrentes": [m.to_dict() for m in modelos],
            "total": len(modelos),
        },
    }), 200


@recorrentes_bp.route("", methods=["POST"])
@login_required
def criar_recorrente():
    """Cadastra um novo modelo de lançamento recorrente."""
    usuario_id = current_user.id
    dados = request.get_json(silent=True) or {}

    tipo = (dados.get("tipo") or "").strip().lower()
    valor_raw = dados.get("valor")
    descricao = (dados.get("descricao") or "").strip()
    categoria_id = dados.get("categoria_id")
    conta_id = dados.get("conta_id")
    forma_pagamento = (dados.get("forma_pagamento") or "PIX").strip()
    dia_vencimento = dados.get("dia_vencimento")
    ativo = dados.get("ativo", True)

    # 1. Validação do tipo
    if tipo not in ("receita", "despesa"):
        return jsonify({
            "sucesso": False,
            "erro": "O tipo do lançamento recorrente deve ser 'receita' ou 'despesa'.",
        }), 400

    # 2. Validação do valor
    if valor_raw is None or valor_raw == "":
        return jsonify({
            "sucesso": False,
            "erro": "O valor é obrigatório.",
        }), 400

    try:
        valor = converter_valor_decimal(valor_raw)
    except (InvalidOperation, ValueError):
        return jsonify({
            "sucesso": False,
            "erro": "Valor inválido. Informe um número decimal positivo.",
        }), 400

    if valor is None or valor <= Decimal("0.00"):
        return jsonify({
            "sucesso": False,
            "erro": "O valor do lançamento recorrente deve ser estritamente maior que zero.",
        }), 400

    # 3. Validação da descrição
    if not descricao or len(descricao) < 2 or len(descricao) > 150:
        return jsonify({
            "sucesso": False,
            "erro": "A descrição é obrigatória e deve ter entre 2 e 150 caracteres.",
        }), 400

    # 4. Validação do dia de vencimento (1 a 31)
    try:
        dia_vencimento = int(dia_vencimento)
    except (TypeError, ValueError):
        return jsonify({
            "sucesso": False,
            "erro": "O dia de vencimento deve ser um número inteiro entre 1 e 31.",
        }), 400

    if dia_vencimento < 1 or dia_vencimento > 31:
        return jsonify({
            "sucesso": False,
            "erro": "O dia de vencimento deve estar entre 1 e 31.",
        }), 400

    # 5. Validação da categoria
    if not categoria_id:
        return jsonify({
            "sucesso": False,
            "erro": "A categoria é obrigatória.",
        }), 400

    categoria = db.session.get(Categoria, categoria_id)
    if not categoria:
        return jsonify({
            "sucesso": False,
            "erro": "Categoria não encontrada.",
        }), 404

    # Proteção IDOR
    if not validar_posse(categoria, "categoria"):
        return jsonify({
            "sucesso": False,
            "erro": "Acesso não autorizado à categoria selecionada.",
        }), 403

    if categoria.tipo != tipo:
        return jsonify({
            "sucesso": False,
            "erro": f"A categoria '{categoria.nome}' é do tipo '{categoria.tipo}', incompatível com a movimentação do tipo '{tipo}'.",
        }), 400

    # 6. Validação da conta
    if not conta_id:
        return jsonify({
            "sucesso": False,
            "erro": "A conta/carteira é obrigatória.",
        }), 400

    conta = db.session.get(Conta, conta_id)
    if not conta:
        return jsonify({
            "sucesso": False,
            "erro": "Conta não encontrada.",
        }), 404

    # Proteção IDOR
    if not validar_posse(conta, "conta"):
        return jsonify({
            "sucesso": False,
            "erro": "Acesso não autorizado à conta selecionada.",
        }), 403

    if conta.status == "arquivado":
        return jsonify({
            "sucesso": False,
            "erro": f"A conta '{conta.nome}' está arquivada e não pode receber novos vínculos recorrentes.",
        }), 400

    # Instancia e persiste o modelo
    novo_modelo = LancamentoRecorrente(
        usuario_id=usuario_id,
        tipo=tipo,
        valor=valor,
        descricao=descricao,
        categoria_id=categoria.id,
        conta_id=conta.id,
        forma_pagamento=forma_pagamento,
        dia_vencimento=dia_vencimento,
        ativo=bool(ativo),
    )

    db.session.add(novo_modelo)
    db.session.commit()

    # Dispara geração automática para o mês corrente caso esteja ativo
    if novo_modelo.ativo:
        try:
            sincronizar_recorrencias_usuario(usuario_id)
        except Exception:
            pass  # Falha eventual de sincronização não impede a criação do modelo

    return jsonify({
        "sucesso": True,
        "mensagem": "Lançamento recorrente cadastrado com sucesso.",
        "dados": {
            "recorrente": novo_modelo.to_dict(),
        },
    }), 201


@recorrentes_bp.route("/<int:id>", methods=["PUT"])
@login_required
def atualizar_recorrente(id: int):
    """Atualiza parâmetros de um modelo recorrente existente."""
    modelo = db.session.get(LancamentoRecorrente, id)
    if not modelo:
        return jsonify({
            "sucesso": False,
            "erro": "Lançamento recorrente não encontrado.",
        }), 404

    # Proteção IDOR
    if not validar_posse(modelo, "recorrente"):
        return jsonify({
            "sucesso": False,
            "erro": "Acesso não autorizado ao lançamento recorrente.",
        }), 403

    dados = request.get_json(silent=True) or {}

    # 1. Tipo
    if "tipo" in dados:
        novo_tipo = (dados["tipo"] or "").strip().lower()
        if novo_tipo not in ("receita", "despesa"):
            return jsonify({
                "sucesso": False,
                "erro": "O tipo deve ser 'receita' ou 'despesa'.",
            }), 400
        modelo.tipo = novo_tipo

    # 2. Valor
    if "valor" in dados:
        valor_raw = dados["valor"]
        try:
            valor = converter_valor_decimal(valor_raw)
        except (InvalidOperation, ValueError):
            return jsonify({
                "sucesso": False,
                "erro": "Valor inválido. Informe um número decimal positivo.",
            }), 400

        if valor is None or valor <= Decimal("0.00"):
            return jsonify({
                "sucesso": False,
                "erro": "O valor deve ser estritamente maior que zero.",
            }), 400
        modelo.valor = valor

    # 3. Descrição
    if "descricao" in dados:
        descricao = (dados["descricao"] or "").strip()
        if not descricao or len(descricao) < 2 or len(descricao) > 150:
            return jsonify({
                "sucesso": False,
                "erro": "A descrição deve ter entre 2 e 150 caracteres.",
            }), 400
        modelo.descricao = descricao

    # 4. Dia de vencimento
    if "dia_vencimento" in dados:
        try:
            dia = int(dados["dia_vencimento"])
        except (TypeError, ValueError):
            return jsonify({
                "sucesso": False,
                "erro": "O dia de vencimento deve ser um número inteiro entre 1 e 31.",
            }), 400

        if dia < 1 or dia > 31:
            return jsonify({
                "sucesso": False,
                "erro": "O dia de vencimento deve estar entre 1 e 31.",
            }), 400
        modelo.dia_vencimento = dia

    # 5. Categoria
    if "categoria_id" in dados:
        cat_id = dados["categoria_id"]
        categoria = db.session.get(Categoria, cat_id)
        if not categoria:
            return jsonify({
                "sucesso": False,
                "erro": "Categoria não encontrada.",
            }), 404
        if not validar_posse(categoria, "categoria"):
            return jsonify({
                "sucesso": False,
                "erro": "Acesso não autorizado à categoria.",
            }), 403

        if categoria.tipo != modelo.tipo:
            return jsonify({
                "sucesso": False,
                "erro": f"A categoria '{categoria.nome}' é do tipo '{categoria.tipo}', incompatível com o tipo '{modelo.tipo}'.",
            }), 400
        modelo.categoria_id = categoria.id

    # 6. Conta
    if "conta_id" in dados:
        c_id = dados["conta_id"]
        conta = db.session.get(Conta, c_id)
        if not conta:
            return jsonify({
                "sucesso": False,
                "erro": "Conta não encontrada.",
            }), 404
        if not validar_posse(conta, "conta"):
            return jsonify({
                "sucesso": False,
                "erro": "Acesso não autorizado à conta.",
            }), 403

        if conta.status == "arquivado":
            return jsonify({
                "sucesso": False,
                "erro": f"A conta '{conta.nome}' está arquivada e não pode ser vinculada.",
            }), 400
        modelo.conta_id = conta.id

    # 7. Forma de pagamento
    if "forma_pagamento" in dados:
        fp = (dados["forma_pagamento"] or "").strip()
        if fp:
            modelo.forma_pagamento = fp

    # 8. Ativo
    if "ativo" in dados:
        modelo.ativo = bool(dados["ativo"])

    db.session.commit()

    return jsonify({
        "sucesso": True,
        "mensagem": "Lançamento recorrente atualizado com sucesso.",
        "dados": {
            "recorrente": modelo.to_dict(),
        },
    }), 200


@recorrentes_bp.route("/<int:id>/toggle", methods=["PATCH"])
@login_required
def alternar_status_recorrente(id: int):
    """Alterna rapidamente o status de atividade (ativo <-> pausado) de um modelo recorrente."""
    modelo = db.session.get(LancamentoRecorrente, id)
    if not modelo:
        return jsonify({
            "sucesso": False,
            "erro": "Lançamento recorrente não encontrado.",
        }), 404

    # Proteção IDOR
    if not validar_posse(modelo, "recorrente"):
        return jsonify({
            "sucesso": False,
            "erro": "Acesso não autorizado ao lançamento recorrente.",
        }), 403

    modelo.ativo = not modelo.ativo
    db.session.commit()

    status_str = "ativado" if modelo.ativo else "pausado"

    # Se foi reativado, sincroniza o mês atual
    if modelo.ativo:
        try:
            sincronizar_recorrencias_usuario(current_user.id)
        except Exception:
            pass

    return jsonify({
        "sucesso": True,
        "mensagem": f"Lançamento recorrente {status_str} com sucesso.",
        "dados": {
            "recorrente": modelo.to_dict(),
        },
    }), 200


@recorrentes_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def excluir_recorrente(id: int):
    """Exclui um modelo recorrente.

    Nota de Integridade (docs/FSD.md - Seções 6.4 e 10.5):
    A exclusão do modelo afeta apenas o molde para ciclos futuros.
    Os lançamentos passados já gerados a partir do modelo permanecem intactos no histórico
    (com recorrente_id = NULL via ON DELETE SET NULL).
    """
    modelo = db.session.get(LancamentoRecorrente, id)
    if not modelo:
        return jsonify({
            "sucesso": False,
            "erro": "Lançamento recorrente não encontrado.",
        }), 404

    # Proteção IDOR
    if not validar_posse(modelo, "recorrente"):
        return jsonify({
            "sucesso": False,
            "erro": "Acesso não autorizado ao lançamento recorrente.",
        }), 403

    db.session.delete(modelo)
    db.session.commit()

    return jsonify({
        "sucesso": True,
        "mensagem": "Lançamento recorrente excluído com sucesso. O histórico de movimentações passadas foi preservado.",
    }), 200


@recorrentes_bp.route("/sincronizar", methods=["POST"])
@login_required
def sincronizar_manualmente():
    """Gatilho para sincronização de fixos em um mês e ano específicos."""
    usuario_id = current_user.id
    dados = request.get_json(silent=True) or {}

    mes = dados.get("mes") or request.args.get("mes", type=int)
    ano = dados.get("ano") or request.args.get("ano", type=int)

    gerados = sincronizar_recorrencias_usuario(usuario_id=usuario_id, ano=ano, mes=mes)

    return jsonify({
        "sucesso": True,
        "mensagem": f"{len(gerados)} lançamento(s) gerado(s) a partir dos modelos recorrentes.",
        "dados": {
            "gerados_total": len(gerados),
            "lancamentos": [l.to_dict() for l in gerados],
        },
    }), 200

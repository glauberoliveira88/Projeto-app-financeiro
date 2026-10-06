"""Controller do Painel Principal / Dashboard do FinançasSimples.

Conforme docs/FSD.md (Seções 6.2, 11.2, 12.3 e 13.4):
- Consolida os três indicadores essenciais do período: Saldo Líquido, Total de Receitas e Total de Despesas.
- Retorna o Saldo Total consolidado de todas as contas ativas.
- Agrupa despesas por categoria de forma monocromática com porcentagem e somatório.
- Fornece bloco de alertas com lançamentos pendentes em atraso e a vencer nos próximos 5 dias.
- Dispara a sincronização transparente de lançamentos recorrentes na virada do ciclo.
- Garante isolamento estrito por usuario_id (anti-IDOR) e exclusão lógica (deleted_at IS NULL).
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from flask import Blueprint, jsonify, request
from sqlalchemy import func, extract, or_, and_

from app.models import db
from app.models.lancamento import Lancamento
from app.models.conta import Conta
from app.models.categoria import Categoria
from app.utils.auth import current_user, login_required
from app.services.recorrentes_service import sincronizar_recorrencias_usuario

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/resumo", methods=["GET"])
@login_required
def obter_resumo_dashboard():
    """Retorna dados consolidados para o Painel Principal do período selecionado.

    Query params:
        mes (int): Mês de competência (1 a 12). Padrão: mês atual.
        ano (int): Ano de competência (ex: 2026). Padrão: ano atual.
    """
    usuario_id = current_user.id
    hoje = date.today()

    mes = request.args.get("mes", type=int)
    ano = request.args.get("ano", type=int)

    if not mes or mes < 1 or mes > 12:
        mes = hoje.month
    if not ano or ano < 2000 or ano > 2100:
        ano = hoje.year

    # 1. Sincronização transparente de lançamentos recorrentes (docs/FSD.md - Seções 6.4 e 13.4)
    try:
        sincronizar_recorrencias_usuario(usuario_id=usuario_id, mes=mes, ano=ano)
    except Exception as e:
        # Falha de sincronização não deve derrubar a visualização do painel
        pass

    # 2. Consulta base de lançamentos do período (excluindo soft-deleted)
    query_mes = Lancamento.query.filter(
        Lancamento.usuario_id == usuario_id,
        Lancamento.deleted_at.is_(None),
        extract("month", Lancamento.data_competencia) == mes,
        extract("year", Lancamento.data_competencia) == ano,
    )

    lancamentos_mes = query_mes.all()

    # 3. Cálculo das Métricas do Mês
    # Conforme FSD Seção 6.2 e 12.3:
    # - Receitas: somatório das receitas do mês (pagas ou previstas)
    # - Despesas: somatório das despesas do mês (pagas ou previstas)
    # - Saldo do Mês: (Receitas Pagas - Despesas Pagas)
    # - Transferências internas não compõem nem alteram o somatório geral de receitas ou de despesas.
    total_receitas = Decimal("0.00")
    total_receitas_pagas = Decimal("0.00")
    total_despesas = Decimal("0.00")
    total_despesas_pagas = Decimal("0.00")

    despesas_por_categoria = {}

    for l in lancamentos_mes:
        if l.tipo == "receita":
            total_receitas += l.valor
            if l.status == "pago":
                total_receitas_pagas += l.valor
        elif l.tipo == "despesa":
            total_despesas += l.valor
            if l.status == "pago":
                total_despesas_pagas += l.valor

            # Agregação para o gráfico de despesas por categoria
            cat_id = l.categoria_id
            cat_nome = l.categoria.nome if l.categoria else "Sem Categoria"
            if cat_id not in despesas_por_categoria:
                despesas_por_categoria[cat_id] = {
                    "categoria_id": cat_id,
                    "nome": cat_nome,
                    "total": Decimal("0.00"),
                }
            despesas_por_categoria[cat_id]["total"] += l.valor

    saldo_mes = total_receitas_pagas - total_despesas_pagas

    # Ordena categorias de despesas pelo total descrescente e calcula percentual
    categorias_grafico = []
    if total_despesas > Decimal("0.00"):
        for item in sorted(despesas_por_categoria.values(), key=lambda x: x["total"], reverse=True):
            pct = (item["total"] / total_despesas) * Decimal("100.0")
            categorias_grafico.append({
                "categoria_id": item["categoria_id"],
                "nome": item["nome"],
                "total": float(item["total"]),
                "porcentagem": round(float(pct), 1),
            })
    else:
        for item in despesas_por_categoria.values():
            categorias_grafico.append({
                "categoria_id": item["categoria_id"],
                "nome": item["nome"],
                "total": float(item["total"]),
                "porcentagem": 0.0,
            })

    # 4. Cálculo do Saldo Total Consolidado de Contas Ativas
    # (Saldo Inicial + Receitas Pagas - Despesas Pagas + Transf Recebidas - Transf Enviadas)
    contas_ativas = Conta.query.filter(
        Conta.usuario_id == usuario_id,
        Conta.status == "ativo"
    ).all()

    saldo_total_contas = Decimal("0.00")
    for c in contas_ativas:
        saldo_total_contas += c.calcular_saldo_atual()

    # 5. Bloco de Alertas de Vencimento (docs/FSD.md - Seções 6.2 e 12.3)
    # Lista rápida de lançamentos pendentes vencidos (data_vencimento < hoje)
    # e que vencem nos próximos 5 dias (hoje <= data_vencimento <= hoje + 5 dias).
    # Alertas são baseados na data corrente real para atenção imediata do usuário.
    data_limite_alerta = hoje + timedelta(days=5)

    alertas_query = Lancamento.query.filter(
        Lancamento.usuario_id == usuario_id,
        Lancamento.deleted_at.is_(None),
        Lancamento.status == "pendente",
        Lancamento.tipo == "despesa",
        Lancamento.data_vencimento <= data_limite_alerta,
    ).order_by(Lancamento.data_vencimento.asc()).all()

    alertas_vencidos = []
    alertas_a_vencer = []

    for item in alertas_query:
        dados_alerta = {
            "id": item.id,
            "descricao": item.descricao,
            "valor": float(item.valor),
            "tipo": item.tipo,
            "categoria": item.categoria.nome if item.categoria else "Sem categoria",
            "conta": item.conta_origem.nome if item.conta_origem else "-",
            "data_vencimento": item.data_vencimento.strftime("%Y-%m-%d"),
            "data_competencia": item.data_competencia.strftime("%Y-%m-%d"),
            "dias_diferenca": (item.data_vencimento - hoje).days,
        }
        if item.data_vencimento < hoje:
            dados_alerta["situacao"] = "vencido"
            alertas_vencidos.append(dados_alerta)
        else:
            dados_alerta["situacao"] = "a_vencer"
            alertas_a_vencer.append(dados_alerta)

    return jsonify({
        "sucesso": True,
        "dados": {
            "periodo": {
                "mes": mes,
                "ano": ano,
            },
            "metricas": {
                "saldo_mes": float(saldo_mes),
                "total_receitas": float(total_receitas),
                "total_receitas_pagas": float(total_receitas_pagas),
                "total_despesas": float(total_despesas),
                "total_despesas_pagas": float(total_despesas_pagas),
                "saldo_total_contas": float(saldo_total_contas),
            },
            "grafico_despesas_categoria": categorias_grafico,
            "alertas": {
                "vencidos": alertas_vencidos,
                "a_vencer": alertas_a_vencer,
                "total_alertas": len(alertas_vencidos) + len(alertas_a_vencer),
            },
        }
    }), 200

"""Serviço de Processamento e Sincronização de Lançamentos Recorrentes (Fixos).

Implementa a automação de geração transparente de movimentações fixas na virada do ciclo mensal
conforme especificado no docs/FSD.md (Seções 6.4, 11.1, 13.4 e 14.2).
"""
import calendar
from datetime import date, datetime
from sqlalchemy import extract

from app.models import db
from app.models.lancamento import Lancamento
from app.models.lancamento_recorrente import LancamentoRecorrente


def sincronizar_recorrencias_usuario(usuario_id: int, ano: int = None, mes: int = None) -> list:
    """Verifica e gera de forma autônoma os lançamentos para modelos recorrentes ativos.

    Regras de Negócio (docs/FSD.md - Seção 13.4):
    1. Consulta se já existem lançamentos gerados para cada modelo ativo no ano/mês solicitado.
    2. Se ainda não gerado (mesmo se soft-deleted para evitar duplicações indevidas), gera novo lançamento:
       - Copia: tipo, valor, descrição, categoria, conta, forma de pagamento.
       - Data de vencimento e competência: ajustada para o último dia válido do mês caso
         o dia_vencimento seja maior que a quantidade de dias do mês (ex: dia 31 em fev/abr).
       - Status inicial: sempre 'pendente'.
       - Vínculo: recorrente_id = modelo.id.
    3. Persiste atomicamente no banco.

    Args:
        usuario_id: ID do usuário autenticado.
        ano: Ano de competência (opcional, padrão: ano atual).
        mes: Mês de competência (opcional, padrão: mês atual).

    Returns:
        Lista com as instâncias de Lancamento geradas nesta execução.
    """
    if not usuario_id:
        return []

    hoje = date.today()
    ano = ano or hoje.year
    mes = mes or hoje.month

    if mes < 1 or mes > 12:
        return []

    # Busca todos os modelos ativos do usuário
    modelos_ativos = (
        LancamentoRecorrente.query
        .filter_by(usuario_id=usuario_id, ativo=True)
        .all()
    )

    if not modelos_ativos:
        return []

    gerados = []

    for modelo in modelos_ativos:
        # Verifica se já existe lançamento vinculado a este modelo no mês/ano (inclusive soft-deletado)
        lancamento_existente = (
            Lancamento.query
            .filter(
                Lancamento.usuario_id == usuario_id,
                Lancamento.recorrente_id == modelo.id,
                extract("year", Lancamento.data_competencia) == ano,
                extract("month", Lancamento.data_competencia) == mes,
            )
            .first()
        )

        if not lancamento_existente:
            # Calcula data com ajuste automático de dias do mês
            data_prevista = modelo.obter_data_vencimento_para_mes(ano, mes)

            novo_lancamento = Lancamento(
                usuario_id=usuario_id,
                tipo=modelo.tipo,
                valor=modelo.valor,
                data_competencia=data_prevista,
                data_vencimento=data_prevista,
                descricao=modelo.descricao,
                categoria_id=modelo.categoria_id,
                conta_id=modelo.conta_id,
                conta_destino_id=None,
                forma_pagamento=modelo.forma_pagamento,
                status="pendente",
                observacao=None,
                recorrente_id=modelo.id,
            )
            db.session.add(novo_lancamento)
            gerados.append(novo_lancamento)

    if gerados:
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    return gerados

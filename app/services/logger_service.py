"""Serviço de Logging Resiliente do FinançasSimples (docs/FSD.md - Seção 19).

Implementa a estratégia de gravação primária em tabelas MySQL (`logs_erros` e
`logs_seguranca`) com mecanismo de contingência automática em arquivo protegido
(`logs/error.log`) caso o banco de dados esteja indisponível ou inacessível.
"""
import sys
import traceback
from flask import current_app, request
from app.models import db, LogErro, LogSeguranca


def registrar_erro(
    nivel: str,
    mensagem: str,
    rota: str = None,
    stack_trace: str = None,
    usuario_id: int = None,
    ip: str = None,
) -> bool:
    """Registra um erro no banco MySQL ou aciona contingência em arquivo em caso de falha."""
    try:
        # Preenchimento automático com dados de contexto da requisição se não fornecidos
        if rota is None and request:
            rota = f"{request.method} {request.path}"
        if ip is None and request:
            ip = request.remote_addr
    except RuntimeError:
        # Fora do contexto de requisição
        pass

    # Destino Primário: Tabela logs_erros no MySQL
    try:
        LogErro.registrar(
            nivel=nivel,
            mensagem=mensagem,
            rota=rota,
            stack_trace=stack_trace,
            usuario_id=usuario_id,
            ip=ip,
        )
        return True
    except Exception as db_err:
        # Contingência Automática: O MySQL falhou, grava no arquivo protegido logs/error.log
        try:
            db.session.rollback()
        except Exception:
            pass

        mensagem_contingencia = (
            f"[CONTINGÊNCIA DE LOG] Falha ao gravar erro no MySQL: {db_err} | "
            f"Erro Original [{nivel}] rota={rota} ip={ip} usuario={usuario_id}: {mensagem}\n"
            f"Stack trace:\n{stack_trace or 'Nenhum'}"
        )
        try:
            current_app.logger.error(mensagem_contingencia)
        except Exception:
            # Fallback extremo para stderr se Flask logger falhar
            sys.stderr.write(f"{mensagem_contingencia}\n")
        return False


def registrar_seguranca(
    evento: str,
    ip: str = None,
    usuario_id: int = None,
    detalhes: str = None,
) -> bool:
    """Registra um evento de segurança no banco MySQL com contingência em arquivo."""
    try:
        if ip is None and request:
            ip = request.remote_addr
    except RuntimeError:
        pass

    try:
        LogSeguranca.registrar(
            evento=evento,
            ip=ip,
            usuario_id=usuario_id,
            detalhes=detalhes,
        )
        return True
    except Exception as db_err:
        try:
            db.session.rollback()
        except Exception:
            pass

        mensagem_contingencia = (
            f"[CONTINGÊNCIA DE SEGURANÇA] Falha ao gravar evento no MySQL: {db_err} | "
            f"Evento: {evento} | IP: {ip} | Usuário: {usuario_id} | Detalhes: {detalhes}"
        )
        try:
            current_app.logger.warning(mensagem_contingencia)
        except Exception:
            sys.stderr.write(f"{mensagem_contingencia}\n")
        return False

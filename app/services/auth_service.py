"""Serviço de Autenticação e Segurança do FinançasSimples (docs/FSD.md - Seções 6.1, 13.1, 15, 16 e 19.2).

Contém a lógica de negócio para autenticação, controle de força bruta, provisionamento
de novos usuários, envio de link de recuperação de senha e verificação de posse.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import logging
from flask import current_app, request
from app.models import (
    db,
    Usuario,
    Conta,
    Categoria,
    LogSeguranca,
)
from app.services.logger_service import registrar_seguranca

logger = logging.getLogger(__name__)

# Lista canônica das 10 categorias padrão iniciais (FSD Seções 6.6 e 13.1.1)
CATEGORIAS_PADRAO = [
    # Receitas
    {"nome": "Salário", "tipo": "receita"},
    {"nome": "Rendimentos", "tipo": "receita"},
    {"nome": "Outras Receitas", "tipo": "receita"},
    # Despesas
    {"nome": "Alimentação", "tipo": "despesa"},
    {"nome": "Moradia", "tipo": "despesa"},
    {"nome": "Transporte", "tipo": "despesa"},
    {"nome": "Saúde", "tipo": "despesa"},
    {"nome": "Educação", "tipo": "despesa"},
    {"nome": "Lazer", "tipo": "despesa"},
    {"nome": "Outras Despesas", "tipo": "despesa"},
]


def provisionar_dados_iniciais_usuario(usuario: Usuario) -> None:
    """Provisiona atomicamente a carteira padrão inicial e as 10 categorias canônicas."""
    # 1. Carteira inicial padrão (FSD Seção 6.1 e 6.5)
    carteira_padrao = Conta(
        usuario_id=usuario.id,
        nome="Carteira",
        saldo_inicial=Decimal("0.00"),
        status="ativo",
    )
    db.session.add(carteira_padrao)

    # 2. As 10 categorias canônicas (FSD Seção 6.6)
    for cat in CATEGORIAS_PADRAO:
        nova_categoria = Categoria(
            usuario_id=usuario.id,
            nome=cat["nome"],
            tipo=cat["tipo"],
            teto_orcamento=None,
            status="ativo",
        )
        db.session.add(nova_categoria)


def verificar_bloqueio_forca_bruta(email: str, ip: str) -> tuple[bool, int]:
    """Verifica se o IP ou e-mail está temporariamente bloqueado por excesso de tentativas falhas.
    
    Regra do FSD (Seções 6 e 15):
    - 5 tentativas de login inválidas consecutivas nos últimos 15 minutos;
    - Bloqueio temporário por 15 minutos.
    
    Retorna (bloqueado: bool, minutos_restantes: int).
    """
    limite_tempo = datetime.now(timezone.utc) - timedelta(minutes=15)
    # Remove tzinfo para compatibilidade com datetime ingênuo do MySQL
    limite_tempo_naive = limite_tempo.replace(tzinfo=None)

    # Consulta tentativas falhas recentes pelo e-mail ou IP
    query = LogSeguranca.query.filter(
        LogSeguranca.evento == "LOGIN_INVALIDO",
        LogSeguranca.created_at >= limite_tempo_naive,
    )
    if email and ip:
        query = query.filter(
            db.or_(
                LogSeguranca.detalhes.ilike(f"%{email}%"),
                LogSeguranca.ip == ip,
            )
        )
    elif email:
        query = query.filter(LogSeguranca.detalhes.ilike(f"%{email}%"))
    elif ip:
        query = query.filter(LogSeguranca.ip == ip)

    total_falhas = query.count()

    if total_falhas >= 5:
        # Busca a tentativa mais recente para calcular tempo restante
        ultimo_log = query.order_by(LogSeguranca.created_at.desc()).first()
        if ultimo_log and ultimo_log.created_at:
            tempo_decorrido = datetime.now(timezone.utc).replace(tzinfo=None) - ultimo_log.created_at
            segundos_restantes = max(0, int(900 - tempo_decorrido.total_seconds()))
            minutos_restantes = max(1, (segundos_restantes + 59) // 60)
            return True, minutos_restantes
        return True, 15

    return False, 0


def despachar_email_recuperacao(usuario: Usuario, token: str) -> bool:
    """Envia o e-mail com link de recuperação de senha ou utiliza fallback seguro no console/log.
    
    Atende ao FSD Seção 15:
    Caso o SMTP não esteja configurado no ambiente de desenvolvimento local, o sistema
    captura de forma transparente e imprime o link completo no console/log.
    """
    url_base = request.host_url.rstrip("/")
    link_recuperacao = f"{url_base}/redefinir-senha/{token}"
    
    mail_username = current_app.config.get("MAIL_USERNAME")
    mail_password = current_app.config.get("MAIL_PASSWORD")
    
    if mail_username and mail_password:
        try:
            from flask_mail import Mail, Message
            mail = Mail(current_app)
            msg = Message(
                subject="FinançasSimples — Recuperação de Senha",
                sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
                recipients=[usuario.email],
            )
            msg.body = (
                f"Olá, {usuario.nome}!\n\n"
                f"Recebemos uma solicitação para redefinir a senha da sua conta no FinançasSimples.\n"
                f"Para prosseguir, utilize o link seguro abaixo (válido por 60 minutos):\n\n"
                f"{link_recuperacao}\n\n"
                f"Se você não solicitou esta alteração, desconsidere esta mensagem. Sua senha permanece inalterada.\n\n"
                f"Atenciosamente,\nEquipe FinançasSimples"
            )
            mail.send(msg)
            return True
        except Exception as e:
            logger.warning(f"Falha ao enviar e-mail via SMTP: {str(e)}. Utilizando contingência de console.")

    # Fallback transparente de desenvolvimento local (FSD Seção 15)
    print("\n" + "=" * 70)
    print("[RECUPERAÇÃO DE SENHA — AMBIENTE DE DESENVOLVIMENTO]")
    print(f"Destinatário: {usuario.nome} <{usuario.email}>")
    print(f"Token (60 min): {token}")
    print(f"Link de Recuperação: {link_recuperacao}")
    print("=" * 70 + "\n")
    current_app.logger.info(
        f"[RECUPERAÇÃO DE SENHA] Link para {usuario.email}: {link_recuperacao}"
    )
    return True

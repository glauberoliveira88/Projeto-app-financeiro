"""Modelo de Conta/Carteira do FinançasSimples (docs/FSD.md - Seções 6.5 e 11.1).

Representa uma carteira ou conta bancária do usuário, encapsulando o cálculo
dinâmico de saldo contábil em tempo real e proteção contra exclusão indevida.
"""
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import func
from app.models import db


def obter_data_hora_utc():
    """Retorna datetime atual em UTC."""
    return datetime.now(timezone.utc)


class Conta(db.Model):
    """Modelo ORM mapeado para a tabela `contas`."""

    __tablename__ = "contas"
    __table_args__ = (
        db.UniqueConstraint("usuario_id", "nome", name="uk_contas_usuario_nome"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nome = db.Column(db.String(100), nullable=False)
    saldo_inicial = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    status = db.Column(
        db.Enum("ativo", "arquivado", name="enum_conta_status"),
        nullable=False,
        default="ativo",
    )
    created_at = db.Column(db.DateTime, nullable=False, default=obter_data_hora_utc)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=obter_data_hora_utc,
        onupdate=obter_data_hora_utc,
    )

    # Relacionamentos
    usuario = db.relationship("Usuario", back_populates="contas")
    lancamentos_origem = db.relationship(
        "Lancamento",
        foreign_keys="Lancamento.conta_id",
        back_populates="conta_origem",
        lazy="dynamic",
    )
    lancamentos_destino = db.relationship(
        "Lancamento",
        foreign_keys="Lancamento.conta_destino_id",
        back_populates="conta_destino",
        lazy="dynamic",
    )
    recorrentes = db.relationship(
        "LancamentoRecorrente",
        back_populates="conta",
        lazy="dynamic",
    )

    def calcular_saldo_atual(self) -> Decimal:
        """Calcula o saldo em tempo real conforme fórmula contábil oficial (FSD Seção 6.5).

        Fórmula: Saldo Inicial + Receitas Pagas - Despesas Pagas
                 + Transferências Recebidas - Transferências Enviadas
        (Sempre filtrando lançamentos não excluídos logicamente).
        """
        from app.models.lancamento import Lancamento

        saldo = Decimal(str(self.saldo_inicial or "0.00"))

        # 1. Total de Receitas Pagas nesta conta
        total_receitas = (
            db.session.query(func.coalesce(func.sum(Lancamento.valor), Decimal("0.00")))
            .filter(
                Lancamento.usuario_id == self.usuario_id,
                Lancamento.conta_id == self.id,
                Lancamento.tipo == "receita",
                Lancamento.status == "pago",
                Lancamento.deleted_at.is_(None),
            )
            .scalar()
        )

        # 2. Total de Despesas Pagas nesta conta
        total_despesas = (
            db.session.query(func.coalesce(func.sum(Lancamento.valor), Decimal("0.00")))
            .filter(
                Lancamento.usuario_id == self.usuario_id,
                Lancamento.conta_id == self.id,
                Lancamento.tipo == "despesa",
                Lancamento.status == "pago",
                Lancamento.deleted_at.is_(None),
            )
            .scalar()
        )

        # 3. Transferências Recebidas (onde esta conta é o destino)
        transf_recebidas = (
            db.session.query(func.coalesce(func.sum(Lancamento.valor), Decimal("0.00")))
            .filter(
                Lancamento.usuario_id == self.usuario_id,
                Lancamento.conta_destino_id == self.id,
                Lancamento.tipo == "transferencia",
                Lancamento.status == "pago",
                Lancamento.deleted_at.is_(None),
            )
            .scalar()
        )

        # 4. Transferências Enviadas (onde esta conta é a origem)
        transf_enviadas = (
            db.session.query(func.coalesce(func.sum(Lancamento.valor), Decimal("0.00")))
            .filter(
                Lancamento.usuario_id == self.usuario_id,
                Lancamento.conta_id == self.id,
                Lancamento.tipo == "transferencia",
                Lancamento.status == "pago",
                Lancamento.deleted_at.is_(None),
            )
            .scalar()
        )

        return (
            saldo
            + Decimal(str(total_receitas))
            - Decimal(str(total_despesas))
            + Decimal(str(transf_recebidas))
            - Decimal(str(transf_enviadas))
        )

    def tem_movimentacoes(self) -> bool:
        """Verifica se a conta possui qualquer movimentação vinculada (ativa ou soft-deletada).

        Regra de integridade: contas com qualquer registro financeiro não podem sofrer
        exclusão física, apenas arquivamento.
        """
        from app.models.lancamento import Lancamento
        from app.models.lancamento_recorrente import LancamentoRecorrente

        # Verifica na tabela lancamentos (origem ou destino, inclusive soft-deletados)
        tem_lancamento = (
            db.session.query(Lancamento.id)
            .filter(
                db.or_(
                    Lancamento.conta_id == self.id,
                    Lancamento.conta_destino_id == self.id,
                )
            )
            .first()
            is not None
        )
        if tem_lancamento:
            return True

        # Verifica na tabela lancamentos_recorrentes
        tem_recorrente = (
            db.session.query(LancamentoRecorrente.id)
            .filter(LancamentoRecorrente.conta_id == self.id)
            .first()
            is not None
        )
        return tem_recorrente

    def arquivar(self) -> None:
        """Define o status da conta como arquivado."""
        self.status = "arquivado"

    def reativar(self) -> None:
        """Define o status da conta como ativo."""
        self.status = "ativo"

    def to_dict(self, incluir_saldo: bool = True) -> dict:
        """Retorna representação em dicionário para respostas JSON da API."""
        saldo_atual = self.calcular_saldo_atual() if incluir_saldo else None
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "nome": self.nome,
            "saldo_inicial": float(self.saldo_inicial) if self.saldo_inicial is not None else 0.0,
            "saldo_atual": float(saldo_atual) if saldo_atual is not None else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Conta id={self.id} usuario_id={self.usuario_id} nome='{self.nome}' status='{self.status}'>"

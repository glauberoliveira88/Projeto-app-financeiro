"""Modelo de Lançamento do FinançasSimples (docs/FSD.md - Seções 6.3 e 11.1).

Representa uma movimentação financeira (receita, despesa ou transferência entre contas),
encapsulando regras de exclusão lógica (soft delete), verificação de vencimentos e alertas.
"""
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
from app.models import db


def obter_data_hora_utc():
    """Retorna datetime atual em UTC."""
    return datetime.now(timezone.utc)


class Lancamento(db.Model):
    """Modelo ORM mapeado para a tabela `lancamentos`."""

    __tablename__ = "lancamentos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo = db.Column(
        db.Enum("receita", "despesa", "transferencia", name="enum_lancamento_tipo"),
        nullable=False,
    )
    valor = db.Column(db.Numeric(12, 2), nullable=False)
    data_competencia = db.Column(db.Date, nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    categoria_id = db.Column(
        db.Integer,
        db.ForeignKey("categorias.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    conta_id = db.Column(
        db.Integer,
        db.ForeignKey("contas.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    conta_destino_id = db.Column(
        db.Integer,
        db.ForeignKey("contas.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    forma_pagamento = db.Column(db.String(50), nullable=False, default="Dinheiro")
    status = db.Column(
        db.Enum("pago", "pendente", name="enum_lancamento_status"),
        nullable=False,
        default="pago",
    )
    observacao = db.Column(db.Text, nullable=True)
    recorrente_id = db.Column(
        db.Integer,
        db.ForeignKey("lancamentos_recorrentes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at = db.Column(db.DateTime, nullable=False, default=obter_data_hora_utc)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=obter_data_hora_utc,
        onupdate=obter_data_hora_utc,
    )
    deleted_at = db.Column(db.DateTime, nullable=True, default=None, index=True)

    # Relacionamentos
    usuario = db.relationship(
        "Usuario",
        back_populates="lancamentos",
        foreign_keys=[usuario_id],
    )
    categoria = db.relationship("Categoria", back_populates="lancamentos")
    conta_origem = db.relationship(
        "Conta",
        foreign_keys=[conta_id],
        back_populates="lancamentos_origem",
    )
    conta_destino = db.relationship(
        "Conta",
        foreign_keys=[conta_destino_id],
        back_populates="lancamentos_destino",
    )
    recorrente = db.relationship("LancamentoRecorrente", back_populates="lancamentos_gerados")

    def soft_delete(self) -> None:
        """Executa exclusão lógica preenchendo o timestamp deleted_at."""
        self.deleted_at = obter_data_hora_utc()

    def restaurar(self) -> None:
        """Restaura um lançamento excluído logicamente."""
        self.deleted_at = None

    @property
    def esta_excluido(self) -> bool:
        """Indica se o lançamento sofreu soft delete."""
        return self.deleted_at is not None

    def esta_vencido(self, hoje: date = None) -> bool:
        """Verifica se o lançamento pendente já passou da data limite de vencimento."""
        if self.status != "pendente" or not self.data_vencimento:
            return False
        dia_atual = hoje or date.today()
        return self.data_vencimento < dia_atual

    def esta_proximo_vencimento(self, dias: int = 5, hoje: date = None) -> bool:
        """Verifica se o lançamento pendente vencerá nos próximos N dias (padrão 5 dias)."""
        if self.status != "pendente" or not self.data_vencimento:
            return False
        dia_atual = hoje or date.today()
        limite = dia_atual + timedelta(days=dias)
        return dia_atual <= self.data_vencimento <= limite

    def to_dict(self) -> dict:
        """Retorna representação em dicionário para respostas JSON da API."""
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "tipo": self.tipo,
            "valor": float(self.valor) if self.valor is not None else 0.0,
            "data_competencia": self.data_competencia.isoformat() if self.data_competencia else None,
            "data_vencimento": self.data_vencimento.isoformat() if self.data_vencimento else None,
            "descricao": self.descricao,
            "categoria_id": self.categoria_id,
            "categoria_nome": self.categoria.nome if self.categoria else None,
            "conta_id": self.conta_id,
            "conta_nome": self.conta_origem.nome if self.conta_origem else None,
            "conta_destino_id": self.conta_destino_id,
            "conta_destino_nome": self.conta_destino.nome if self.conta_destino else None,
            "forma_pagamento": self.forma_pagamento,
            "status": self.status,
            "observacao": self.observacao,
            "recorrente_id": self.recorrente_id,
            "vencido": self.esta_vencido(),
            "alerta_proximo": self.esta_proximo_vencimento(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<Lancamento id={self.id} usuario_id={self.usuario_id} tipo='{self.tipo}' "
            f"valor={self.valor} status='{self.status}' deleted={self.esta_excluido}>"
        )

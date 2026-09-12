"""Modelo de Lançamento Recorrente do FinançasSimples (docs/FSD.md - Seções 6.4 e 11.1).

Representa um modelo de receita ou despesa fixa que se repete mensalmente,
encapsulando o cálculo do dia de vencimento com ajuste automático para meses curtos.
"""
import calendar
from datetime import datetime, date, timezone
from decimal import Decimal
from app.models import db


def obter_data_hora_utc():
    """Retorna datetime atual em UTC."""
    return datetime.now(timezone.utc)


class LancamentoRecorrente(db.Model):
    """Modelo ORM mapeado para a tabela `lancamentos_recorrentes`."""

    __tablename__ = "lancamentos_recorrentes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo = db.Column(
        db.Enum("receita", "despesa", name="enum_recorrente_tipo"),
        nullable=False,
    )
    valor = db.Column(db.Numeric(12, 2), nullable=False)
    descricao = db.Column(db.String(150), nullable=False)
    categoria_id = db.Column(
        db.Integer,
        db.ForeignKey("categorias.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    conta_id = db.Column(
        db.Integer,
        db.ForeignKey("contas.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    forma_pagamento = db.Column(db.String(50), nullable=False, default="PIX")
    dia_vencimento = db.Column(db.SmallInteger, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=obter_data_hora_utc)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=obter_data_hora_utc,
        onupdate=obter_data_hora_utc,
    )

    # Relacionamentos
    usuario = db.relationship("Usuario", back_populates="lancamentos_recorrentes")
    categoria = db.relationship("Categoria", back_populates="recorrentes")
    conta = db.relationship("Conta", back_populates="recorrentes")
    lancamentos_gerados = db.relationship(
        "Lancamento",
        back_populates="recorrente",
        lazy="dynamic",
    )

    def obter_data_vencimento_para_mes(self, ano: int, mes: int) -> date:
        """Calcula a data de vencimento no mês/ano, ajustando se o mês for mais curto (ex: dia 31 em fev/abr)."""
        _, ultimo_dia = calendar.monthrange(ano, mes)
        dia_ajustado = min(self.dia_vencimento, ultimo_dia)
        return date(ano, mes, dia_ajustado)

    def to_dict(self) -> dict:
        """Retorna representação em dicionário para respostas JSON da API."""
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "tipo": self.tipo,
            "valor": float(self.valor) if self.valor is not None else 0.0,
            "descricao": self.descricao,
            "categoria_id": self.categoria_id,
            "categoria_nome": self.categoria.nome if self.categoria else None,
            "conta_id": self.conta_id,
            "conta_nome": self.conta.nome if self.conta else None,
            "forma_pagamento": self.forma_pagamento,
            "dia_vencimento": self.dia_vencimento,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<LancamentoRecorrente id={self.id} usuario_id={self.usuario_id} "
            f"descricao='{self.descricao}' dia={self.dia_vencimento} ativo={self.ativo}>"
        )

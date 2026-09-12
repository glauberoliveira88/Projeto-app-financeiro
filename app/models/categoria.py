"""Modelo de Categoria do FinançasSimples (docs/FSD.md - Seções 6.6 e 11.1).

Representa uma categoria de receita ou despesa do usuário, encapsulando o teto
de gastos orçamentário, verificação de movimentações e controle de inativação lógica.
"""
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import func, extract
from app.models import db


def obter_data_hora_utc():
    """Retorna datetime atual em UTC."""
    return datetime.now(timezone.utc)


class Categoria(db.Model):
    """Modelo ORM mapeado para a tabela `categorias`."""

    __tablename__ = "categorias"
    __table_args__ = (
        db.UniqueConstraint(
            "usuario_id", "nome", "tipo", name="uk_categorias_usuario_nome_tipo"
        ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(
        db.Enum("receita", "despesa", name="enum_categoria_tipo"),
        nullable=False,
    )
    teto_orcamento = db.Column(db.Numeric(12, 2), nullable=True, default=None)
    status = db.Column(
        db.Enum("ativo", "arquivado", name="enum_categoria_status"),
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
    usuario = db.relationship("Usuario", back_populates="categorias")
    lancamentos = db.relationship(
        "Lancamento",
        back_populates="categoria",
        lazy="dynamic",
    )
    recorrentes = db.relationship(
        "LancamentoRecorrente",
        back_populates="categoria",
        lazy="dynamic",
    )

    def consumo_mes(self, ano: int, mes: int) -> Decimal:
        """Calcula o valor total consumido por despesas pagas no mês e ano informados."""
        from app.models.lancamento import Lancamento

        if self.tipo != "despesa":
            return Decimal("0.00")

        total = (
            db.session.query(func.coalesce(func.sum(Lancamento.valor), Decimal("0.00")))
            .filter(
                Lancamento.usuario_id == self.usuario_id,
                Lancamento.categoria_id == self.id,
                Lancamento.tipo == "despesa",
                Lancamento.status == "pago",
                Lancamento.deleted_at.is_(None),
                extract("year", Lancamento.data_competencia) == ano,
                extract("month", Lancamento.data_competencia) == mes,
            )
            .scalar()
        )
        return Decimal(str(total))

    def porcentagem_consumo(self, ano: int, mes: int) -> float:
        """Calcula o percentual de atingimento do teto de orçamento no mês informado."""
        if not self.teto_orcamento or Decimal(str(self.teto_orcamento)) <= Decimal("0.00"):
            return 0.0

        consumo = self.consumo_mes(ano, mes)
        teto = Decimal(str(self.teto_orcamento))
        porcentagem = (consumo / teto) * Decimal("100.0")
        return round(float(porcentagem), 2)

    def tem_movimentacoes(self) -> bool:
        """Verifica se existem lançamentos ou modelos recorrentes vinculados a esta categoria."""
        from app.models.lancamento import Lancamento
        from app.models.lancamento_recorrente import LancamentoRecorrente

        tem_lancamento = (
            db.session.query(Lancamento.id)
            .filter(Lancamento.categoria_id == self.id)
            .first()
            is not None
        )
        if tem_lancamento:
            return True

        tem_recorrente = (
            db.session.query(LancamentoRecorrente.id)
            .filter(LancamentoRecorrente.categoria_id == self.id)
            .first()
            is not None
        )
        return tem_recorrente

    def arquivar(self) -> None:
        """Define o status da categoria como arquivado."""
        self.status = "arquivado"

    def reativar(self) -> None:
        """Define o status da categoria como ativo."""
        self.status = "ativo"

    def to_dict(self, ano: int = None, mes: int = None, incluir_consumo: bool = False) -> dict:
        """Retorna representação em dicionário para respostas JSON da API."""
        dados = {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "nome": self.nome,
            "tipo": self.tipo,
            "teto_orcamento": float(self.teto_orcamento) if self.teto_orcamento is not None else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if incluir_consumo and ano and mes:
            consumo = self.consumo_mes(ano, mes)
            porcentagem = self.porcentagem_consumo(ano, mes)
            dados["consumo_mes"] = float(consumo)
            dados["porcentagem_consumo"] = porcentagem
            dados["teto_excedido"] = bool(
                self.teto_orcamento and consumo > Decimal(str(self.teto_orcamento))
            )

        return dados

    def __repr__(self) -> str:
        return f"<Categoria id={self.id} usuario_id={self.usuario_id} nome='{self.nome}' tipo='{self.tipo}'>"

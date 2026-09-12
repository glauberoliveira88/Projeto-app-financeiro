"""Modelo de Log de Erro do FinançasSimples (docs/FSD.md - Seções 11.1 e 19.1).

Representa os registros de falhas técnicas não tratadas e exceções operacionais
estruturadas no banco de dados MySQL.
"""
from datetime import datetime, timezone
from app.models import db


def obter_data_hora_utc():
    """Retorna datetime atual em UTC."""
    return datetime.now(timezone.utc)


class LogErro(db.Model):
    """Modelo ORM mapeado para a tabela `logs_erros`."""

    __tablename__ = "logs_erros"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    nivel = db.Column(db.String(20), nullable=False, default="ERROR")
    rota = db.Column(db.String(255), nullable=True)
    mensagem = db.Column(db.Text, nullable=False)
    stack_trace = db.Column(db.Text, nullable=True)
    ip = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=obter_data_hora_utc)

    # Relacionamento com Usuário
    usuario = db.relationship("Usuario", back_populates="logs_erros")

    @classmethod
    def registrar(
        cls,
        nivel: str,
        mensagem: str,
        rota: str = None,
        stack_trace: str = None,
        usuario_id: int = None,
        ip: str = None,
    ) -> "LogErro":
        """Persiste um novo registro de erro no banco MySQL."""
        novo_log = cls(
            nivel=nivel.upper(),
            mensagem=str(mensagem),
            rota=rota,
            stack_trace=stack_trace,
            usuario_id=usuario_id,
            ip=ip,
        )
        db.session.add(novo_log)
        db.session.commit()
        return novo_log

    def to_dict(self) -> dict:
        """Retorna representação em dicionário."""
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "nivel": self.nivel,
            "rota": self.rota,
            "mensagem": self.mensagem,
            "ip": self.ip,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<LogErro id={self.id} nivel='{self.nivel}' rota='{self.rota}'>"

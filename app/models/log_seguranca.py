"""Modelo de Log de Segurança do FinançasSimples (docs/FSD.md - Seções 11.1 e 19.2).

Representa os eventos de segurança do sistema, como falhas de autenticação,
bloqueios de força bruta e tentativas de violação de IDOR.
"""
from datetime import datetime, timezone
from app.models import db


def obter_data_hora_utc():
    """Retorna datetime atual em UTC."""
    return datetime.now(timezone.utc)


class LogSeguranca(db.Model):
    """Modelo ORM mapeado para a tabela `logs_seguranca`."""

    __tablename__ = "logs_seguranca"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    evento = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(45), nullable=True)
    detalhes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=obter_data_hora_utc)

    # Relacionamento com Usuário
    usuario = db.relationship("Usuario", back_populates="logs_seguranca")

    @classmethod
    def registrar(
        cls,
        evento: str,
        ip: str = None,
        usuario_id: int = None,
        detalhes: str = None,
    ) -> "LogSeguranca":
        """Persiste um novo evento de segurança estruturado no banco."""
        novo_log = cls(
            evento=evento.upper(),
            ip=ip,
            usuario_id=usuario_id,
            detalhes=str(detalhes) if detalhes is not None else None,
        )
        db.session.add(novo_log)
        db.session.commit()
        return novo_log

    def to_dict(self) -> dict:
        """Retorna representação em dicionário."""
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "evento": self.evento,
            "ip": self.ip,
            "detalhes": self.detalhes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<LogSeguranca id={self.id} evento='{self.evento}' ip='{self.ip}'>"

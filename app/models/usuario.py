"""Modelo de Usuário do FinançasSimples (docs/FSD.md - Seções 6.1 e 11.1).

Representa a entidade de usuários do sistema, encapsulando regras de autenticação,
hashing de senhas, recuperação por token e isolamento de tenant.
"""
from datetime import datetime, timedelta, timezone
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db


def obter_data_hora_utc():
    """Retorna datetime atual em UTC."""
    return datetime.now(timezone.utc)


class Usuario(db.Model):
    """Modelo ORM mapeado para a tabela `usuarios`."""
    
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(191), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True, index=True)
    tema_preferido = db.Column(
        db.Enum("dark", "light", name="enum_tema_preferido"),
        nullable=False,
        default="dark",
    )
    token_recuperacao = db.Column(db.String(100), nullable=True)
    token_recuperacao_expira = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=obter_data_hora_utc)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=obter_data_hora_utc,
        onupdate=obter_data_hora_utc,
    )

    # Relacionamentos
    contas = db.relationship(
        "Conta",
        back_populates="usuario",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    categorias = db.relationship(
        "Categoria",
        back_populates="usuario",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    lancamentos = db.relationship(
        "Lancamento",
        back_populates="usuario",
        foreign_keys="Lancamento.usuario_id",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    lancamentos_recorrentes = db.relationship(
        "LancamentoRecorrente",
        back_populates="usuario",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    logs_erros = db.relationship(
        "LogErro",
        back_populates="usuario",
        lazy="dynamic",
    )
    logs_seguranca = db.relationship(
        "LogSeguranca",
        back_populates="usuario",
        lazy="dynamic",
    )

    def definir_senha(self, senha: str) -> None:
        """Criptografa e armazena o hash seguro da senha com sal."""
        if not senha or len(senha) < 8:
            raise ValueError("A senha deve conter no mínimo 8 caracteres.")
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha: str) -> bool:
        """Valida a senha informada contra o hash armazenado."""
        if not self.senha_hash or not senha:
            return False
        return check_password_hash(self.senha_hash, senha)

    def gerar_token_recuperacao(self, horas_validade: int = 1) -> str:
        """Gera e define um token seguro de recuperação de senha com validade."""
        token = secrets.token_urlsafe(32)
        self.token_recuperacao = token
        self.token_recuperacao_expira = obter_data_hora_utc() + timedelta(hours=horas_validade)
        return token

    def validar_token_recuperacao(self, token: str) -> bool:
        """Verifica se o token informado é idêntico e se ainda está no prazo de validade."""
        if not self.token_recuperacao or not token:
            return False
        if not self.token_recuperacao_expira:
            return False
        # Converte para timezone-aware se necessário para comparação precisa
        agora = obter_data_hora_utc()
        expira = self.token_recuperacao_expira
        if expira.tzinfo is None:
            agora = agora.replace(tzinfo=None)
        if agora > expira:
            return False
        return secrets.compare_digest(self.token_recuperacao, token)

    def limpar_token_recuperacao(self) -> None:
        """Invalida o token de recuperação após o uso bem-sucedido."""
        self.token_recuperacao = None
        self.token_recuperacao_expira = None

    # Propriedades de compatibilidade com gerenciamento de autenticação / sessão
    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> str:
        return str(self.id)

    def to_dict(self) -> dict:
        """Retorna uma representação em dicionário sem expor informações sensíveis."""
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "tema_preferido": self.tema_preferido or "dark",
            "is_google_user": bool(self.google_id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} email='{self.email}'>"

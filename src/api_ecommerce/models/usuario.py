from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from api_ecommerce.database.base import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True,
    )

    celular: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    cpf: Mapped[str] = mapped_column(
        String(11),
        nullable=False,
        unique=True,
    )
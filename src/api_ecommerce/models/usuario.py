from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_ecommerce.database.base import Base

if TYPE_CHECKING:
    from api_ecommerce.models.endereco import Endereco


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
        unique=True,
    )

    cpf: Mapped[str | None] = mapped_column(
        String(11),
        nullable=True,
        unique=True,
    )

    enderecos: Mapped[list["Endereco"]] = relationship(
        back_populates="usuario",
        cascade="all, delete-orphan",
    )
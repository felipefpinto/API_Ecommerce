from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from api_ecommerce.database.base import Base


if TYPE_CHECKING:
    from api_ecommerce.models.produto import Produto
    from api_ecommerce.models.complemento import Complemento


class GrupoComplemento(Base):
    __tablename__ = "grupo_complemento"

    id_grupo: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    id_restaurante: Mapped[int] = mapped_column(
    ForeignKey(
        "restaurante.id_restaurante",
        ondelete="CASCADE",
    ),
    nullable=False,
    index=True,
)

    nome: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    descricao: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    obrigatorio: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    min_selecoes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    max_selecoes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    ordem: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    produtos: Mapped[list["Produto"]] = relationship(
        secondary="produto_grupo_complemento",
        back_populates="grupos_complemento",
        viewonly=True,
    )

    complementos: Mapped[list["Complemento"]] = relationship(
        back_populates="grupo",
        cascade="all, delete-orphan",
    )
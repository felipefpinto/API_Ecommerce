from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
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
    from api_ecommerce.models.grupo_complemento import GrupoComplemento


class Complemento(Base):
    __tablename__ = "complemento"

    id_complemento: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    id_grupo: Mapped[int] = mapped_column(
        ForeignKey(
            "grupo_complemento.id_grupo",
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

    preco_adicional: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
        server_default="0",
    )

    disponivel: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    estoque: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
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

    grupo: Mapped["GrupoComplemento"] = relationship(
        back_populates="complementos",
    )
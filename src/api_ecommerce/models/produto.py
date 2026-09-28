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
    from api_ecommerce.models.restaurante import Restaurante
    from api_ecommerce.models.secao_cardapio import SecaoCardapio
    from api_ecommerce.models.grupo_complemento import GrupoComplemento


class Produto(Base):
    __tablename__ = "produto"

    id_produto: Mapped[int] = mapped_column(
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
        String(500),
        nullable=True,
    )

    preco_base: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    imagem_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
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

    serve_pessoas: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
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

    restaurante: Mapped["Restaurante"] = relationship(
        back_populates="produtos",
    )

    secoes: Mapped[list["SecaoCardapio"]] = relationship(
        secondary="secao_produto",
        viewonly=True,
    )
    grupos_complemento: Mapped[list["GrupoComplemento"]] = relationship(
        secondary="produto_grupo_complemento",
        back_populates="produtos",
        viewonly=True,
)
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from api_ecommerce.database.base import Base


if TYPE_CHECKING:
    from api_ecommerce.models.usuario import Usuario
    from api_ecommerce.models.restaurante import Restaurante
    from api_ecommerce.models.produto import Produto
    from api_ecommerce.models.complemento import Complemento


class Carrinho(Base):
    __tablename__ = "carrinho"

    id_carrinho: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id_usuario"),
        nullable=False,
        index=True,
    )

    id_restaurante: Mapped[int] = mapped_column(
        ForeignKey("restaurante.id_restaurante"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ATIVO",
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

    itens: Mapped[list["CarrinhoItem"]] = relationship(
        back_populates="carrinho",
        cascade="all, delete-orphan",
    )


class CarrinhoItem(Base):
    __tablename__ = "carrinho_item"

    id_item: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    id_carrinho: Mapped[int] = mapped_column(
        ForeignKey(
            "carrinho.id_carrinho",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    id_produto: Mapped[int] = mapped_column(
        ForeignKey("produto.id_produto"),
        nullable=False,
        index=True,
    )

    quantidade: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    preco_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    observacao: Mapped[str | None] = mapped_column(
        Text,
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

    carrinho: Mapped["Carrinho"] = relationship(
        back_populates="itens",
    )

    complementos: Mapped[
        list["CarrinhoItemComplemento"]
    ] = relationship(
        back_populates="item",
        cascade="all, delete-orphan",
    )


class CarrinhoItemComplemento(Base):
    __tablename__ = "carrinho_item_complemento"

    id_item_complemento: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    id_item: Mapped[int] = mapped_column(
        ForeignKey(
            "carrinho_item.id_item",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    id_complemento: Mapped[int] = mapped_column(
        ForeignKey("complemento.id_complemento"),
        nullable=False,
        index=True,
    )

    quantidade: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    preco_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    item: Mapped["CarrinhoItem"] = relationship(
        back_populates="complementos",
    )
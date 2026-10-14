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
    from api_ecommerce.models.endereco import Endereco
    from api_ecommerce.models.produto import Produto
    from api_ecommerce.models.complemento import Complemento


class Pedido(Base):
    __tablename__ = "pedido"

    id_pedido: Mapped[int] = mapped_column(
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

    id_endereco: Mapped[int | None] = mapped_column(
        ForeignKey("endereco.id_endereco"),
        nullable=True,
        index=True,
    )

    endereco_cep: Mapped[str | None] = mapped_column(
    String(8),
    nullable=True,
    )

    endereco_logradouro: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    endereco_numero: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    endereco_complemento: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    endereco_bairro: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    endereco_cidade: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    endereco_uf: Mapped[str | None] = mapped_column(
        String(2),
        nullable=True,
    )

    endereco_ponto_referencia: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="AGUARDANDO_PAGAMENTO",
        server_default="AGUARDANDO_PAGAMENTO",
        index=True,
    )

    tipo_entrega: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ENTREGA",
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    taxa_entrega: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    desconto: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    valor_total: Mapped[Decimal] = mapped_column(
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

    usuario: Mapped["Usuario"] = relationship()

    restaurante: Mapped["Restaurante"] = relationship()

    endereco: Mapped["Endereco | None"] = relationship()

    itens: Mapped[list["ItemPedido"]] = relationship(
        back_populates="pedido",
        cascade="all, delete-orphan",
    )

    pagamentos: Mapped[list["Pagamento"]] = relationship(
        back_populates="pedido",
        cascade="all, delete-orphan",
    )


class ItemPedido(Base):
    __tablename__ = "item_pedido"

    id_item_pedido: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    id_pedido: Mapped[int] = mapped_column(
        ForeignKey(
            "pedido.id_pedido",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    id_produto: Mapped[int | None] = mapped_column(
        ForeignKey("produto.id_produto"),
        nullable=True,
        index=True,
    )

    nome_produto: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    quantidade: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    preco_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    subtotal: Mapped[Decimal] = mapped_column(
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

    pedido: Mapped["Pedido"] = relationship(
        back_populates="itens",
    )

    produto: Mapped["Produto | None"] = relationship()

    complementos: Mapped[
        list["ItemPedidoComplemento"]
    ] = relationship(
        back_populates="item",
        cascade="all, delete-orphan",
    )


class ItemPedidoComplemento(Base):
    __tablename__ = "item_pedido_complemento"

    id_item_pedido_complemento: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    id_item_pedido: Mapped[int] = mapped_column(
        ForeignKey(
            "item_pedido.id_item_pedido",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    id_complemento: Mapped[int | None] = mapped_column(
        ForeignKey("complemento.id_complemento"),
        nullable=True,
        index=True,
    )

    nome_complemento: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
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

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    item: Mapped["ItemPedido"] = relationship(
        back_populates="complementos",
    )

    complemento: Mapped["Complemento | None"] = relationship()


class Pagamento(Base):
    __tablename__ = "pagamento"

    id_pagamento: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    id_pedido: Mapped[int] = mapped_column(
        ForeignKey(
            "pedido.id_pedido",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    metodo: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDENTE",
        server_default="PENDENTE",
        index=True,
    )

    valor: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    mercado_pago_order_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        index=True,
    )

    mercado_pago_payment_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        index=True,
    )

    external_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        index=True,
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

    pedido: Mapped["Pedido"] = relationship(
        back_populates="pagamentos",
    )
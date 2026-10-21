from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
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


class ConfiguracaoEntrega(Base):
    __tablename__ = "configuracao_entrega"

    id_configuracao: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    id_restaurante: Mapped[int] = mapped_column(
        ForeignKey(
            "restaurante.id_restaurante",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    raio_entrega_km: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    valor_minimo_pedido: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )

    entrega_gratis: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    valor_minimo_entrega_gratis: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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
        back_populates="configuracao_entrega",
    )

    faixas: Mapped[list["FaixaEntrega"]] = relationship(
        back_populates="configuracao",
        cascade="all, delete-orphan",
        order_by="FaixaEntrega.ordem",
    )


class FaixaEntrega(Base):
    __tablename__ = "faixa_entrega"

    id_faixa: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    id_configuracao: Mapped[int] = mapped_column(
        ForeignKey(
            "configuracao_entrega.id_configuracao",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    distancia_min_km: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    distancia_max_km: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    taxa: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    ordem: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
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

    configuracao: Mapped["ConfiguracaoEntrega"] = relationship(
        back_populates="faixas",
    )
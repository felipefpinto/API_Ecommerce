from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
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
    from api_ecommerce.models.secao_cardapio import (SecaoCardapio,
)


class Cardapio(Base):
    __tablename__ = "cardapio"

    id_cardapio: Mapped[int] = mapped_column(
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
        String(100),
        nullable=False,
    )

    descricao: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
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
        back_populates="cardapios",
    )
    secoes: Mapped[list["SecaoCardapio"]] = relationship(
    back_populates="cardapio",
    cascade="all, delete-orphan",
)
from __future__ import annotations

from datetime import datetime

from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_ecommerce.database.base import Base

if TYPE_CHECKING:
    from api_ecommerce.models.categorias_restaurante import Categorias_restaurante
    from api_ecommerce.models.restaurante import Restaurante

class RestauranteCategoria(Base):
    __tablename__ = "restaurante_categoria"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    restaurante_id: Mapped[int] = mapped_column(
        ForeignKey(
            "restaurante.id_restaurante",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    categoria_id: Mapped[int] = mapped_column(
        ForeignKey(
            "categoria.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    restaurante: Mapped["Restaurante"] = relationship()

    categoria: Mapped["Categorias_restaurante"] = relationship()

    __table_args__ = (
        UniqueConstraint(
            "restaurante_id",
            "categoria_id",
            name="uq_restaurante_categoria"
        ),

        Index(
            "idx_rc_categoria_id",
            "categoria_id"
        ),

        Index(
            "idx_rc_restaurante_id",
            "restaurante_id"
        ),
    )
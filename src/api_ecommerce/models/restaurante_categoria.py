from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from api_ecommerce.database.base import Base


class RestauranteCategoria(Base):
    __tablename__ = "restaurante_categoria"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    restaurante_id: Mapped[int] = mapped_column(
        ForeignKey(
            "restaurante.id",
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
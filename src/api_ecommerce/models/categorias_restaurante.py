from datetime import datetime

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from api_ecommerce.database.base import Base


class Categorias_restaurante(Base):
    __tablename__ = "categoria"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    nome: Mapped[str] = mapped_column(
        String(80),
        nullable=False
    )

    descricao: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="ATIVA",
        server_default="ATIVA"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    __table_args__ = (
        Index(
            "uq_categoria_nome",
            func.lower(nome),
            unique=True
        ),
        Index(
            "idx_categoria_status",
            "status"
        ),
        Index(
            "idx_categoria_created_at",
            "created_at"
        ),
    )
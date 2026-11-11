from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from api_ecommerce.database.base import Base


class SecaoProduto(Base):
    __tablename__ = "secao_produto"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    id_secao: Mapped[int] = mapped_column(
        ForeignKey(
            "secao_cardapio.id_secao",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    id_produto: Mapped[int] = mapped_column(
        ForeignKey(
            "produto.id_produto",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    preco: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    ordem: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
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

    __table_args__ = (
        UniqueConstraint(
            "id_secao",
            "id_produto",
            name="uq_secao_produto",
        ),
    )
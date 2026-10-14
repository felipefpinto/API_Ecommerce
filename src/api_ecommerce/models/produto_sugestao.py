from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_ecommerce.database.base import Base

if TYPE_CHECKING:
    from api_ecommerce.models.produto import Produto


class ProdutoSugestao(Base):
    __tablename__ = "produto_sugestao"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    id_produto: Mapped[int] = mapped_column(
        ForeignKey(
            "produto.id_produto",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    id_produto_sugerido: Mapped[int] = mapped_column(
        ForeignKey(
            "produto.id_produto",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    ordem: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    produto: Mapped["Produto"] = relationship(
        foreign_keys=[id_produto],
    )

    produto_sugerido: Mapped["Produto"] = relationship(
        foreign_keys=[id_produto_sugerido],
    )

    __table_args__ = (
        UniqueConstraint(
            "id_produto",
            "id_produto_sugerido",
            name="uq_produto_sugestao",
        ),
    )
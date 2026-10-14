from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from api_ecommerce.database.base import Base


if TYPE_CHECKING:
    from api_ecommerce.models.produto import Produto
    from api_ecommerce.models.grupo_complemento import GrupoComplemento


class ProdutoGrupoComplemento(Base):
    __tablename__ = "produto_grupo_complemento"

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

    id_grupo: Mapped[int] = mapped_column(
        ForeignKey(
            "grupo_complemento.id_grupo",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    produto: Mapped["Produto"] = relationship()

    grupo: Mapped["GrupoComplemento"] = relationship()

    __table_args__ = (
        UniqueConstraint(
            "id_produto",
            "id_grupo",
            name="uq_produto_grupo_complemento",
        ),
    )
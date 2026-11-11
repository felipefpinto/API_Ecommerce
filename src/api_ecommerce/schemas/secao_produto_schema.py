from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
)


class SecaoProdutoCreate(BaseModel):
    id_produto: int

    preco: Decimal | None = Field(
        default=None,
        gt=0,
    )

    ordem: int = Field(
        default=0,
        ge=0,
    )


class SecaoProdutoUpdate(BaseModel):
    preco: Decimal | None = Field(
        default=None,
        gt=0,
    )

    ordem: int | None = Field(
        default=None,
        ge=0,
    )

    ativo: bool | None = None


class SecaoProdutoResponse(BaseModel):
    id: int
    id_secao: int
    id_produto: int

    preco: Decimal | None
    ordem: int
    ativo: bool

    model_config = {
        "from_attributes": True
    }
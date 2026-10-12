from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
)


class ProdutoCreate(BaseModel):
    nome: str = Field(
        ...,
        min_length=1,
        max_length=120,
    )

    descricao: str | None = Field(
        default=None,
        max_length=500,
    )

    preco_base: Decimal = Field(
        ...,
        gt=0,
    )

    estoque: int | None = Field(
        default=None,
        ge=0,
    )

    serve_pessoas: int | None = Field(
        default=None,
        ge=1,
    )


class ProdutoUpdate(BaseModel):
    nome: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
    )

    descricao: str | None = Field(
        default=None,
        max_length=500,
    )

    preco_base: Decimal | None = Field(
        default=None,
        gt=0,
    )

    estoque: int | None = Field(
        default=None,
        ge=0,
    )

    serve_pessoas: int | None = Field(
        default=None,
        ge=1,
    )

    disponivel: bool | None = None
    ativo: bool | None = None


class ProdutoResponse(BaseModel):
    id_produto: int
    id_restaurante: int

    nome: str
    descricao: str | None

    preco_base: Decimal

    imagem_url: str | None

    disponivel: bool
    ativo: bool

    estoque: int | None
    serve_pessoas: int | None

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
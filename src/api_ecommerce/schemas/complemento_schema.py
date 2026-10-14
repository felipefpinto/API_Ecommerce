from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ComplementoCreate(BaseModel):
    nome: str = Field(
        ...,
        min_length=1,
        max_length=120,
    )

    descricao: str | None = Field(
        default=None,
        max_length=255,
    )

    preco_adicional: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
    )

    estoque: int | None = Field(
        default=None,
        ge=0,
    )

    ordem: int = Field(
        default=0,
        ge=0,
    )


class ComplementoUpdate(BaseModel):
    nome: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
    )

    descricao: str | None = Field(
        default=None,
        max_length=255,
    )

    preco_adicional: Decimal | None = Field(
        default=None,
        ge=0,
    )

    estoque: int | None = Field(
        default=None,
        ge=0,
    )

    disponivel: bool | None = None
    ativo: bool | None = None

    ordem: int | None = Field(
        default=None,
        ge=0,
    )


class ComplementoResponse(BaseModel):
    id_complemento: int
    id_grupo: int

    nome: str
    descricao: str | None

    preco_adicional: Decimal

    disponivel: bool
    ativo: bool

    estoque: int | None
    ordem: int

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
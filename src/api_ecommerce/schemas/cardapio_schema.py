from datetime import datetime

from pydantic import BaseModel, Field


class CardapioCreate(BaseModel):
    nome: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    descricao: str | None = Field(
        default=None,
        max_length=300,
    )


class CardapioUpdate(BaseModel):
    nome: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    descricao: str | None = Field(
        default=None,
        max_length=300,
    )

    ativo: bool | None = None


class CardapioResponse(BaseModel):
    id_cardapio: int
    id_restaurante: int
    nome: str
    descricao: str | None
    ativo: bool

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
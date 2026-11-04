from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
)


class SecaoCardapioCreate(BaseModel):
    nome: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    descricao: str | None = Field(
        default=None,
        max_length=300,
    )

    ordem: int = Field(
        default=0,
        ge=0,
    )


class SecaoCardapioUpdate(BaseModel):
    nome: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    descricao: str | None = Field(
        default=None,
        max_length=300,
    )

    ordem: int | None = Field(
        default=None,
        ge=0,
    )

    ativo: bool | None = None


class SecaoCardapioResponse(BaseModel):
    id_secao: int
    id_cardapio: int

    nome: str
    descricao: str | None

    ordem: int
    ativo: bool

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
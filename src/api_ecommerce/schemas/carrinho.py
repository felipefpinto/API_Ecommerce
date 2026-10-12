from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# =========================================================
# COMPLEMENTO DO ITEM
# =========================================================

class CarrinhoItemComplementoCreate(BaseModel):
    id_complemento: int

    quantidade: int = Field(
        default=1,
        ge=1,
    )


class CarrinhoItemComplementoResponse(BaseModel):
    id_item_complemento: int
    id_complemento: int

    nome_complemento: str | None = None

    quantidade: int
    preco_unitario: Decimal

    model_config = {"from_attributes": True}



# =========================================================
# ITEM DO CARRINHO
# =========================================================

class CarrinhoItemCreate(BaseModel):
    id_produto: int

    quantidade: int = Field(
        ...,
        ge=1,
    )

    observacao: str | None = Field(
        default=None,
        max_length=250,
    )

    complementos: list[CarrinhoItemComplementoCreate] = Field(
        default_factory=list,
    )


class CarrinhoItemUpdate(BaseModel):
    quantidade: int | None = Field(
        default=None,
        ge=1,
    )

    observacao: str | None = Field(
        default=None,
        max_length=250,
    )
class CarrinhoQuantidadeUpdate(BaseModel):
    quantidade: int = Field(
        ...,
        ge=1,
    )

class CarrinhoItemResponse(BaseModel):
    id_item: int
    id_produto: int

    nome_produto: str | None = None
    imagem_url: str | None = None

    quantidade: int
    preco_unitario: Decimal
    observacao: str | None

    complementos: list[CarrinhoItemComplementoResponse] = Field(
        default_factory=list
    )

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}



# =========================================================
# ADICIONAR ITEM AO CARRINHO
# =========================================================

class CarrinhoAdicionarItem(BaseModel):
    id_restaurante: int
    id_produto: int

    quantidade: int = Field(
        ...,
        ge=1,
    )

    observacao: str | None = Field(
        default=None,
        max_length=250,
    )

    complementos: list[CarrinhoItemComplementoCreate] = Field(
        default_factory=list,
    )


# =========================================================
# CARRINHO
# =========================================================

class CarrinhoResponse(BaseModel):
    id_carrinho: int
    id_usuario: int
    id_restaurante: int

    nome_restaurante: str | None = None
    logo_restaurante: str | None = None

    status: str

    itens: list[CarrinhoItemResponse] = Field(
        default_factory=list
    )

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


# =========================================================
# CRIAR PEDIDO
# =========================================================

class PedidoCreate(BaseModel):
    id_endereco: int | None = None

    tipo_entrega: str = Field(
        default="ENTREGA",
        max_length=20,
    )

    observacao: str | None = Field(
        default=None,
        max_length=500,
    )


# =========================================================
# COMPLEMENTO DO ITEM DO PEDIDO
# =========================================================

class ItemPedidoComplementoResponse(BaseModel):
    id_item_pedido_complemento: int
    id_complemento: int | None

    nome_complemento: str

    quantidade: int
    preco_unitario: Decimal
    subtotal: Decimal

    model_config = {
        "from_attributes": True
    }


# =========================================================
# ITEM DO PEDIDO
# =========================================================

class ItemPedidoResponse(BaseModel):
    id_item_pedido: int
    id_produto: int | None

    nome_produto: str

    quantidade: int
    preco_unitario: Decimal
    subtotal: Decimal

    observacao: str | None

    complementos: list[
        ItemPedidoComplementoResponse
    ] = Field(
        default_factory=list
    )

    created_at: datetime

    model_config = {
        "from_attributes": True
    }


# =========================================================
# PAGAMENTO
# =========================================================

class PagamentoResponse(BaseModel):
    id_pagamento: int

    metodo: str
    status: str

    valor: Decimal

    mercado_pago_order_id: str | None
    mercado_pago_payment_id: str | None
    external_reference: str | None

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# =========================================================
# PEDIDO
# =========================================================

class PedidoResponse(BaseModel):
    id_pedido: int

    id_usuario: int
    id_restaurante: int
    id_endereco: int | None

    nome_restaurante: str | None = None
    logo_restaurante: str | None = None

    status: str
    tipo_entrega: str

    subtotal: Decimal
    taxa_entrega: Decimal
    desconto: Decimal
    valor_total: Decimal

    observacao: str | None

    # Snapshot do endereço
    endereco_cep: str | None = None
    endereco_logradouro: str | None = None
    endereco_numero: str | None = None
    endereco_complemento: str | None = None
    endereco_bairro: str | None = None
    endereco_cidade: str | None = None
    endereco_uf: str | None = None
    endereco_ponto_referencia: str | None = None

    itens: list[ItemPedidoResponse] = Field(
        default_factory=list
    )

    pagamentos: list[PagamentoResponse] = Field(
        default_factory=list
    )

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class PedidoStatusUpdate(BaseModel):
    status: Literal[
        "EM_PREPARO",
        "PRONTO",
        "SAIU_PARA_ENTREGA",
        "ENTREGUE",
    ]
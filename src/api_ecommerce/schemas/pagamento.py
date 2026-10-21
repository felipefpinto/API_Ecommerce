from pydantic import BaseModel, Field


class PagamentoPixResponse(BaseModel):
    id_pagamento: int
    id_pedido: int

    metodo: str
    status: str

    mercado_pago_order_id: str

    qr_code: str | None = None
    qr_code_base64: str | None = None
    ticket_url: str | None = None


class PagamentoCartaoCreate(BaseModel):
    token: str = Field(min_length=1)
    payment_method_id: str = Field(min_length=1)
    installments: int = Field(ge=1)
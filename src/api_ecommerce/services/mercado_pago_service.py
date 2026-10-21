from decimal import Decimal
from uuid import uuid4

import httpx
from fastapi import HTTPException, status

from api_ecommerce.core.config import settings


MERCADO_PAGO_BASE_URL = "https://api.mercadopago.com"


def _headers(idempotency_key: str | None = None) -> dict[str, str]:
    if not settings.mercado_pago_access_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Access Token do Mercado Pago não configurado.",
        )

    headers = {
        "Authorization": f"Bearer {settings.mercado_pago_access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if idempotency_key:
        headers["X-Idempotency-Key"] = idempotency_key

    return headers


def criar_order_pix(
    *,
    id_pedido: int,
    valor_total: Decimal,
    email_usuario: str,
) -> dict:

    idempotency_key = str(uuid4())

    payload = {
        "type": "online",
        "processing_mode": "automatic",
        "external_reference": f"PEDIDO-{id_pedido}",
        "total_amount": f"{valor_total:.2f}",
        "payer": {
            "email": email_usuario,
            "first_name": "APRO"
        },
        "transactions": {
            "payments": [
                {
                    "amount": f"{valor_total:.2f}",
                    "payment_method": {
                        "id": "pix",
                        "type": "bank_transfer",
                    },
                }
            ]
        },
    }

    try:
        response = httpx.post(
            f"{MERCADO_PAGO_BASE_URL}/v1/orders",
            headers=_headers(idempotency_key),
            json=payload,
            timeout=30.0,
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível conectar ao Mercado Pago.",
        ) from exc

    if response.status_code not in (200, 201):
        try:
            erro = response.json()
        except ValueError:
            erro = response.text

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "mensagem": "Erro ao criar pagamento Pix no Mercado Pago.",
                "mercado_pago": erro,
            },
        )

    return response.json()

def criar_order_cartao(
    *,
    id_pedido: int,
    valor_total: Decimal,
    email_usuario: str,
    token_cartao: str,
    payment_method_id: str,
    parcelas: int,
) -> dict:

    if not token_cartao:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token do cartão não informado.",
        )

    if not payment_method_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meio de pagamento do cartão não informado.",
        )

    if parcelas < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantidade de parcelas inválida.",
        )

    idempotency_key = str(uuid4())

    payload = {
        "type": "online",
        "processing_mode": "automatic",
        "external_reference": f"PEDIDO-{id_pedido}",
        "total_amount": f"{valor_total:.2f}",
        "payer": {
            "email": email_usuario,
        },
        "transactions": {
            "payments": [
                {
                    "amount": f"{valor_total:.2f}",
                    "payment_method": {
                        "id": payment_method_id,
                        "type": "credit_card",
                        "token": token_cartao,
                        "installments": parcelas,
                    },
                }
            ]
        },
    }

    try:
        response = httpx.post(
            f"{MERCADO_PAGO_BASE_URL}/v1/orders",
            headers=_headers(idempotency_key),
            json=payload,
            timeout=30.0,
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível conectar ao Mercado Pago.",
        ) from exc

    if response.status_code not in (200, 201):
        try:
            erro = response.json()
        except ValueError:
            erro = response.text

        # ---------------------------------------------------------
        # Cartão recusado
        # ---------------------------------------------------------
        # O Mercado Pago pode criar a Order, mas retornar a
        # transação como failed.
        #
        # Isso é uma recusa de pagamento válida e não uma falha
        # de comunicação com o Mercado Pago.
        # ---------------------------------------------------------

        if isinstance(erro, dict):
            order = erro.get("data")

            if (
                isinstance(order, dict)
                and order.get("status") == "failed"
            ):
                return order

        # ---------------------------------------------------------
        # Erro realmente inesperado
        # ---------------------------------------------------------

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "mensagem": "Erro ao criar pagamento com cartão no Mercado Pago.",
                "mercado_pago": erro,
            },
        )

    return response.json()

def buscar_order(order_id: str) -> dict:
    try:
        response = httpx.get(
            f"{MERCADO_PAGO_BASE_URL}/v1/orders/{order_id}",
            headers=_headers(),
            timeout=30.0,
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível consultar a Order no Mercado Pago.",
        ) from exc

    if response.status_code != 200:
        try:
            erro = response.json()
        except ValueError:
            erro = response.text

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "mensagem": "Erro ao consultar a Order no Mercado Pago.",
                "mercado_pago": erro,
            },
        )

    return response.json()
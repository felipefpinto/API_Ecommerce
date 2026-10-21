import hashlib
import hmac

from fastapi import HTTPException, status
from mercadopago.webhook import (
    WebhookSignatureValidator,
    InvalidWebhookSignatureError,
)

from api_ecommerce.core.config import settings


def validar_assinatura_mercado_pago(
    *,
    x_signature: str | None,
    x_request_id: str | None,
    data_id: str | None,
) -> None:
    if not settings.mercado_pago_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chave secreta do webhook do Mercado Pago não configurada.",
        )

    if not x_signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Assinatura do Mercado Pago não informada.",
        )

    secret = settings.mercado_pago_webhook_secret
    print("Tamanho da Webhook Secret:", len(secret))
    print(
        "Secret possui espaços nas extremidades:",
        secret != secret.strip(),
    )
    print(
        "Webhook Secret carregado:",
        hashlib.sha256(
            secret.encode("utf-8")
        ).hexdigest()[:8],
    )
    try:
        WebhookSignatureValidator.validate(
            x_signature,
            x_request_id,
            data_id,
            settings.mercado_pago_webhook_secret,
        )

    except InvalidWebhookSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Assinatura do Mercado Pago inválida.",
        )

def diagnosticar_assinatura_mercado_pago(
    *,
    x_signature: str | None,
    x_request_id: str | None,
    data_id: str | None,
) -> None:
    if (
        not x_signature
        or not x_request_id
        or not data_id
        or not settings.mercado_pago_webhook_secret
    ):
        print("=== DIAGNÓSTICO ASSINATURA ===")
        print("Dados insuficientes para diagnóstico.")
        return

    partes = {}

    for parte in x_signature.split(","):
        if "=" in parte:
            chave, valor = parte.split("=", 1)
            partes[chave.strip()] = valor.strip()

    ts = partes.get("ts")
    v1_recebido = partes.get("v1")

    if not ts or not v1_recebido:
        print("=== DIAGNÓSTICO ASSINATURA ===")
        print("x-signature sem ts ou v1.")
        return

    def calcular(candidate_id: str) -> str:
        manifest = (
            f"id:{candidate_id};"
            f"request-id:{x_request_id};"
            f"ts:{ts};"
        )

        return hmac.new(
            settings.mercado_pago_webhook_secret.encode("utf-8"),
            manifest.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    assinatura_original = calcular(data_id)
    assinatura_lowercase = calcular(data_id.lower())

    print("=== DIAGNÓSTICO ASSINATURA ===")
    print(
        "HMAC original:",
        hmac.compare_digest(
            assinatura_original,
            v1_recebido,
        ),
    )
    print(
        "HMAC lowercase:",
        hmac.compare_digest(
            assinatura_lowercase,
            v1_recebido,
        ),
    )
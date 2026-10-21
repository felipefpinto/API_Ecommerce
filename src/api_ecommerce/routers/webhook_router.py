from api_ecommerce.controllers import pagamento_controller
from api_ecommerce.database.connection import get_db
from sqlalchemy.orm import Session
from typing import Any

from fastapi import APIRouter, Body, Depends, Request

from api_ecommerce.services.mercado_pago_service import buscar_order

from api_ecommerce.services.webhook_service import (
    validar_assinatura_mercado_pago,
    diagnosticar_assinatura_mercado_pago,
)

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


@router.post("/mercado-pago")
async def webhook_mercado_pago(
    request: Request,
    body: dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    x_signature = request.headers.get("x-signature")
    x_request_id = request.headers.get("x-request-id")

    # DEBUG TEMPORÁRIO
    print("=== WEBHOOK RECEBIDO ===")
    print("data.id:", request.query_params.get("data.id"))
    print("x-request-id:", x_request_id)
    print("x-signature:", x_signature)

    # O Mercado Pago normalmente envia o ID também
    # como query param: ?data.id=ORD...
    data_id = request.query_params.get("data.id")

    # Fallback para o body
    if not data_id:
        data = body.get("data")

        if isinstance(data, dict):
            data_id = data.get("id")

    data_id_assinatura = (
        data_id.lower()
        if isinstance(data_id, str)
        else data_id
    )

    diagnosticar_assinatura_mercado_pago(
        x_signature=x_signature,
        x_request_id=x_request_id,
        data_id=data_id_assinatura,
    )

    validar_assinatura_mercado_pago(
        x_signature=x_signature,
        x_request_id=x_request_id,
        data_id=data_id_assinatura,
    )

    if not data_id:
        return {
            "recebido": True,
            "mensagem": "Notificação sem Data ID.",
        }

    order = buscar_order(data_id)

    resultado = pagamento_controller.processar_webhook_order(
        db=db,
        order=order,
    )

    print("=== ORDER CONSULTADA NO MERCADO PAGO ===")
    print("ID:", order.get("id"))
    print("Status:", order.get("status"))
    print("Status detail:", order.get("status_detail"))
    print("External reference:", order.get("external_reference"))

    return {
        "recebido": True,
        "assinatura_valida": True,
        "resultado": resultado,
    }
        
'''@router.post("/mercado-pago/processar-order/{order_id}")
def processar_order_teste(
    order_id: str,
    db: Session = Depends(get_db),
):
    order = buscar_order(order_id)

    resultado = pagamento_controller.processar_webhook_order(
        db=db,
        order=order,
    )

    return {
        "order": {
            "id": order.get("id"),
            "status": order.get("status"),
            "status_detail": order.get("status_detail"),
            "external_reference": order.get("external_reference"),
        },
        "resultado": resultado,'''
    
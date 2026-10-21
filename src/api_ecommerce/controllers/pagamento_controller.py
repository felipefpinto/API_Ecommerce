from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api_ecommerce.models.pedido import Pagamento
from api_ecommerce.models.usuario import Usuario
from api_ecommerce.controllers import pedido_controller
from api_ecommerce.services.mercado_pago_service import (
    criar_order_pix,
    criar_order_cartao,
    buscar_order,
)


def criar_pagamento_pix(
    db: Session,
    id_usuario: int,
    id_pedido: int,
) -> dict:

    # ---------------------------------------------------------
    # 1. Busca o pedido e garante que pertence ao usuário
    # ---------------------------------------------------------

    pedido = pedido_controller.buscar_pedido_usuario(
        db=db,
        id_usuario=id_usuario,
        id_pedido=id_pedido,
    )

    # ---------------------------------------------------------
    # 2. Pedido precisa estar aguardando pagamento
    # ---------------------------------------------------------

    if pedido.status != "AGUARDANDO_PAGAMENTO":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este pedido não está aguardando pagamento.",
        )

    # ---------------------------------------------------------
    # 3. Evita criar outro pagamento para o mesmo pedido
    # ---------------------------------------------------------

    pagamento_existente = db.scalar(
        select(Pagamento).where(
            Pagamento.id_pedido == id_pedido,
            Pagamento.status == "PENDENTE",
        )
    )

    if pagamento_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um pagamento pendente para este pedido.",
        )

    # ---------------------------------------------------------
    # 4. Busca usuário
    # ---------------------------------------------------------

    usuario = db.get(
        Usuario,
        id_usuario,
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    if not usuario.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O usuário precisa possuir um e-mail para realizar o pagamento.",
        )

    # ---------------------------------------------------------
    # 5. Cria Order Pix no Mercado Pago
    # ---------------------------------------------------------

    order = criar_order_pix(
        id_pedido=pedido.id_pedido,
        valor_total=pedido.valor_total,
        email_usuario=usuario.email,
    )

    # ---------------------------------------------------------
    # 6. Extrai dados retornados pelo Mercado Pago
    # ---------------------------------------------------------

    mercado_pago_order_id = order.get("id")

    payments = (
        order.get("transactions", {})
        .get("payments", [])
    )

    if not mercado_pago_order_id or not payments:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resposta inválida recebida do Mercado Pago.",
        )

    payment_mp = payments[0]

    mercado_pago_payment_id = payment_mp.get("id")

    payment_method = payment_mp.get(
        "payment_method",
        {},
    )

    qr_code = payment_method.get("qr_code")
    qr_code_base64 = payment_method.get("qr_code_base64")
    ticket_url = payment_method.get("ticket_url")

    # ---------------------------------------------------------
    # 7. Salva pagamento local
    # ---------------------------------------------------------

    pagamento = Pagamento(
        id_pedido=pedido.id_pedido,
        metodo="PIX",
        status="PENDENTE",
        valor=pedido.valor_total,
        mercado_pago_order_id=mercado_pago_order_id,
        mercado_pago_payment_id=mercado_pago_payment_id,
        external_reference=f"PEDIDO-{pedido.id_pedido}",
    )

    try:
        db.add(pagamento)

        db.commit()
        db.refresh(pagamento)

    except Exception:
        db.rollback()
        raise

    # ---------------------------------------------------------
    # 8. Retorna dados necessários para o frontend
    # ---------------------------------------------------------

    return {
        "id_pagamento": pagamento.id_pagamento,
        "id_pedido": pedido.id_pedido,
        "metodo": pagamento.metodo,
        "status": pagamento.status,
        "mercado_pago_order_id": mercado_pago_order_id,
        "qr_code": qr_code,
        "qr_code_base64": qr_code_base64,
        "ticket_url": ticket_url,
    }

def criar_pagamento_cartao(
    db: Session,
    id_usuario: int,
    id_pedido: int,
    token_cartao: str,
    payment_method_id: str,
    parcelas: int,
) -> dict:

    # ---------------------------------------------------------
    # 1. Busca pedido e valida proprietário
    # ---------------------------------------------------------

    pedido = pedido_controller.buscar_pedido_usuario(
        db=db,
        id_usuario=id_usuario,
        id_pedido=id_pedido,
    )

    if pedido.status != "AGUARDANDO_PAGAMENTO":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este pedido não está aguardando pagamento.",
        )

    # ---------------------------------------------------------
    # 2. Verifica pagamento pendente existente
    # ---------------------------------------------------------

    pagamento_existente = db.scalar(
        select(Pagamento).where(
            Pagamento.id_pedido == id_pedido,
            Pagamento.status == "PENDENTE",
        )
    )

    if pagamento_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um pagamento pendente para este pedido.",
        )

    # ---------------------------------------------------------
    # 3. Busca usuário
    # ---------------------------------------------------------

    usuario = db.get(
        Usuario,
        id_usuario,
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    if not usuario.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O usuário precisa possuir um e-mail para realizar o pagamento.",
        )

    # ---------------------------------------------------------
    # 4. Cria Order de cartão no Mercado Pago
    # ---------------------------------------------------------

    order = criar_order_cartao(
        id_pedido=pedido.id_pedido,
        valor_total=pedido.valor_total,
        email_usuario=usuario.email,
        token_cartao=token_cartao,
        payment_method_id=payment_method_id,
        parcelas=parcelas,
    )

    # ---------------------------------------------------------
    # 5. Extrai retorno da Order
    # ---------------------------------------------------------

    mercado_pago_order_id = order.get("id")

    payments = (
        order.get("transactions", {})
        .get("payments", [])
    )

    if not mercado_pago_order_id or not payments:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resposta inválida recebida do Mercado Pago.",
        )

    payment_mp = payments[0]

    mercado_pago_payment_id = payment_mp.get("id")

    # ---------------------------------------------------------
    # 6. Descobre o status retornado pelo Mercado Pago
    # ---------------------------------------------------------

    order_status = order.get("status")
    status_detail = order.get("status_detail")

    if (
        order_status == "processed"
        and status_detail == "accredited"
    ):
        status_pagamento = "APROVADO"

    elif order_status == "action_required":
        status_pagamento = "PENDENTE"

    else:
        status_pagamento = "RECUSADO"

    # ---------------------------------------------------------
    # 7. Salva pagamento local
    # ---------------------------------------------------------

    pagamento = Pagamento(
        id_pedido=pedido.id_pedido,
        metodo="CARTAO",
        status=status_pagamento,
        valor=pedido.valor_total,
        mercado_pago_order_id=mercado_pago_order_id,
        mercado_pago_payment_id=mercado_pago_payment_id,
        external_reference=f"PEDIDO-{pedido.id_pedido}",
    )

    # Se já veio aprovado, o restaurante já pode receber
    # o pedido para aceite.
    if status_pagamento == "APROVADO":
        pedido.status = "AGUARDANDO_ACEITE"

    try:
        db.add(pagamento)
        db.commit()
        db.refresh(pagamento)
        db.refresh(pedido)

    except Exception:
        db.rollback()
        raise

    # ---------------------------------------------------------
    # 8. Resposta para o frontend
    # ---------------------------------------------------------

    return {
        "id_pagamento": pagamento.id_pagamento,
        "id_pedido": pedido.id_pedido,
        "metodo": pagamento.metodo,
        "status": pagamento.status,
        "status_pedido": pedido.status,
        "mercado_pago_order_id": mercado_pago_order_id,
        "mercado_pago_payment_id": mercado_pago_payment_id,
        "order_status": order_status,
        "status_detail": status_detail,
    }

def processar_webhook_order(
    db: Session,
    order: dict,
) -> dict:
    order_id = order.get("id")
    external_reference = order.get("external_reference")
    order_status = order.get("status")
    status_detail = order.get("status_detail")

    if not order_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order do Mercado Pago sem ID.",
        )

    pagamento = db.scalar(
        select(Pagamento).where(
            Pagamento.mercado_pago_order_id == str(order_id)
        )
    )

    if not pagamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento não encontrado para esta Order.",
        )

    pedido = pedido_controller.buscar_pedido_por_id(
        db=db,
        id_pedido=pagamento.id_pedido,
    )

    # Segurança adicional:
    # a external_reference da Order precisa apontar para o mesmo pedido.
    external_reference_esperada = f"PEDIDO-{pedido.id_pedido}"

    if external_reference != external_reference_esperada:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="External reference da Order não corresponde ao pedido.",
        )

    # PIX criado, mas ainda aguardando pagamento.
    if (
        order_status == "action_required"
        and status_detail == "waiting_transfer"
    ):
        pagamento.status = "PENDENTE"

        # Não regredimos um pedido que já tenha avançado.
        if pedido.status == "AGUARDANDO_PAGAMENTO":
            pedido.status = "AGUARDANDO_PAGAMENTO"

    # Pagamento confirmado.
    elif (
        order_status == "processed"
        and status_detail == "accredited"
    ):
        pagamento.status = "APROVADO"

        # Idempotência:
        # só avançamos se ele ainda estiver aguardando pagamento.
        if pedido.status == "AGUARDANDO_PAGAMENTO":
            pedido.status = "AGUARDANDO_ACEITE"

    db.commit()
    db.refresh(pagamento)
    db.refresh(pedido)

    return {
        "id_pagamento": pagamento.id_pagamento,
        "status_pagamento": pagamento.status,
        "id_pedido": pedido.id_pedido,
        "status_pedido": pedido.status,
        "mercado_pago_order_id": pagamento.mercado_pago_order_id,
        "order_status": order_status,
        "status_detail": status_detail,
    }

def sincronizar_pagamento_pedido(
    db: Session,
    id_usuario: int,
    id_pedido: int,
) -> dict:

    pedido = pedido_controller.buscar_pedido_usuario(
        db=db,
        id_usuario=id_usuario,
        id_pedido=id_pedido,
    )

    pagamento = db.scalar(
        select(Pagamento)
        .where(
            Pagamento.id_pedido == pedido.id_pedido,
            Pagamento.mercado_pago_order_id.is_not(None),
        )
        .order_by(Pagamento.id_pagamento.desc())
    )

    if not pagamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento do Mercado Pago não encontrado para este pedido.",
        )

    order = buscar_order(
        pagamento.mercado_pago_order_id
    )

    return processar_webhook_order(
        db=db,
        order=order,
    )
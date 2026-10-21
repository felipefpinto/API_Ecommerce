from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api_ecommerce.controllers import pagamento_controller
from api_ecommerce.database.connection import get_db
from api_ecommerce.schemas.pagamento import (
    PagamentoPixResponse,
    PagamentoCartaoCreate,
)


router = APIRouter(
    prefix="/usuarios/{id_usuario}/pedidos/{id_pedido}/pagamentos",
    tags=["Pagamentos"],
)


@router.post(
    "/pix",
    response_model=PagamentoPixResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_pagamento_pix(
    id_usuario: int,
    id_pedido: int,
    db: Session = Depends(get_db),
):
    return pagamento_controller.criar_pagamento_pix(
        db=db,
        id_usuario=id_usuario,
        id_pedido=id_pedido,
    )

@router.post("/sincronizar")
def sincronizar_pagamento(
    id_usuario: int,
    id_pedido: int,
    db: Session = Depends(get_db),
):
    return pagamento_controller.sincronizar_pagamento_pedido(
        db=db,
        id_usuario=id_usuario,
        id_pedido=id_pedido,
    )

@router.post(
    "/cartao",
    status_code=status.HTTP_201_CREATED,
)
def criar_pagamento_cartao(
    id_usuario: int,
    id_pedido: int,
    dados: PagamentoCartaoCreate,
    db: Session = Depends(get_db),
):
    return pagamento_controller.criar_pagamento_cartao(
        db=db,
        id_usuario=id_usuario,
        id_pedido=id_pedido,
        token_cartao=dados.token,
        payment_method_id=dados.payment_method_id,
        parcelas=dados.installments,
    )
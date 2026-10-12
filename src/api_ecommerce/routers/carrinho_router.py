from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.orm import Session

from api_ecommerce.controllers import carrinho_controller
from api_ecommerce.database.connection import ( get_db,)
from api_ecommerce.schemas.carrinho import (
    CarrinhoAdicionarItem,
    CarrinhoQuantidadeUpdate,
    CarrinhoResponse,
)


router = APIRouter(
    prefix="/usuarios/{id_usuario}/carrinho",
    tags=["Carrinho"],
)


# =========================================================
# OBTER CARRINHO
# =========================================================

@router.get(
    "",
    response_model=CarrinhoResponse,
)
def obter_carrinho(
    id_usuario: int,
    db: Session = Depends(get_db),
):
    return carrinho_controller.obter_carrinho(
        db=db,
        id_usuario=id_usuario,
    )


# =========================================================
# ADICIONAR ITEM
# =========================================================

@router.post(
    "/itens",
    response_model=CarrinhoResponse,
    status_code=status.HTTP_201_CREATED,
)
def adicionar_item(
    id_usuario: int,
    dados: CarrinhoAdicionarItem,
    db: Session = Depends(get_db),
):
    return carrinho_controller.adicionar_item(
        db=db,
        id_usuario=id_usuario,
        dados=dados,
    )


# =========================================================
# ALTERAR QUANTIDADE
# =========================================================

@router.patch(
    "/itens/{id_item}",
    response_model=CarrinhoResponse,
)
def alterar_quantidade(
    id_usuario: int,
    id_item: int,
    dados: CarrinhoQuantidadeUpdate,
    db: Session = Depends(get_db),
):
    return carrinho_controller.alterar_quantidade_item(
        db=db,
        id_usuario=id_usuario,
        id_item=id_item,
        quantidade=dados.quantidade,
    )


# =========================================================
# REMOVER ITEM
# =========================================================

@router.delete(
    "/itens/{id_item}",
)
def remover_item(
    id_usuario: int,
    id_item: int,
    db: Session = Depends(get_db),
):
    carrinho = carrinho_controller.remover_item(
        db=db,
        id_usuario=id_usuario,
        id_item=id_item,
    )

    if carrinho is None:
        return {
            "mensagem": "Item removido. O carrinho ficou vazio."
        }

    return carrinho


# =========================================================
# ESVAZIAR CARRINHO
# =========================================================

@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
)
def esvaziar_carrinho(
    id_usuario: int,
    db: Session = Depends(get_db),
):
    carrinho_controller.esvaziar_carrinho(
        db=db,
        id_usuario=id_usuario,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


# =========================================================
# SUBSTITUIR CARRINHO
# =========================================================

@router.post(
    "/substituir",
    response_model=CarrinhoResponse,
    status_code=status.HTTP_201_CREATED,
)
def substituir_carrinho(
    id_usuario: int,
    dados: CarrinhoAdicionarItem,
    db: Session = Depends(get_db),
):
    return carrinho_controller.substituir_carrinho(
        db=db,
        id_usuario=id_usuario,
        dados=dados,
    )
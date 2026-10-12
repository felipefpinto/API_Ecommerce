from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from api_ecommerce.controllers import (
    cardapio_controller,
)
from api_ecommerce.database.connection import (
    get_db,
)
from api_ecommerce.schemas.cardapio_schema import (
    CardapioCreate,
    CardapioResponse,
    CardapioUpdate,
)


router = APIRouter(
    prefix="/restaurantes/{id_restaurante}/cardapios",
    tags=["Cardápios"],
)


@router.post(
    "/",
    response_model=CardapioResponse,
)
def criar_cardapio(
    id_restaurante: int,
    dados: CardapioCreate,
    db: Session = Depends(get_db),
):
    return (
        cardapio_controller
        .criar_cardapio(
            db,
            id_restaurante,
            dados,
        )
    )


@router.get(
    "/",
    response_model=list[
        CardapioResponse
    ],
)
def listar_cardapios(
    id_restaurante: int,
    db: Session = Depends(get_db),
):
    return (
        cardapio_controller
        .listar_cardapios(
            db,
            id_restaurante,
        )
    )


@router.get(
    "/{id_cardapio}",
    response_model=CardapioResponse,
)
def buscar_cardapio(
    id_restaurante: int,
    id_cardapio: int,
    db: Session = Depends(get_db),
):
    return (
        cardapio_controller
        .buscar_cardapio(
            db,
            id_restaurante,
            id_cardapio,
        )
    )


@router.patch(
    "/{id_cardapio}",
    response_model=CardapioResponse,
)
def atualizar_cardapio(
    id_restaurante: int,
    id_cardapio: int,
    dados: CardapioUpdate,
    db: Session = Depends(get_db),
):
    return (
        cardapio_controller
        .atualizar_cardapio(
            db,
            id_restaurante,
            id_cardapio,
            dados,
        )
    )


@router.delete(
    "/{id_cardapio}",
)
def deletar_cardapio(
    id_restaurante: int,
    id_cardapio: int,
    db: Session = Depends(get_db),
):
    return (
        cardapio_controller
        .deletar_cardapio(
            db,
            id_restaurante,
            id_cardapio,
        )
    )
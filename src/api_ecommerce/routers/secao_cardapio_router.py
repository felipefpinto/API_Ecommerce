from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from api_ecommerce.controllers import (
    secao_cardapio_controller,
)
from api_ecommerce.database.connection import (
    get_db,
)
from api_ecommerce.schemas.secao_cardapio_schema import (
    SecaoCardapioCreate,
    SecaoCardapioResponse,
    SecaoCardapioUpdate,
)


router = APIRouter(
    prefix=(
        "/restaurantes/"
        "{id_restaurante}/"
        "cardapios/"
        "{id_cardapio}/"
        "secoes"
    ),
    tags=["Seções do Cardápio"],
)


@router.post(
    "/",
    response_model=SecaoCardapioResponse,
)
def criar_secao(
    id_restaurante: int,
    id_cardapio: int,
    dados: SecaoCardapioCreate,
    db: Session = Depends(get_db),
):
    return (
        secao_cardapio_controller
        .criar_secao(
            db,
            id_restaurante,
            id_cardapio,
            dados,
        )
    )


@router.get(
    "/",
    response_model=list[
        SecaoCardapioResponse
    ],
)
def listar_secoes(
    id_restaurante: int,
    id_cardapio: int,
    db: Session = Depends(get_db),
):
    return (
        secao_cardapio_controller
        .listar_secoes(
            db,
            id_restaurante,
            id_cardapio,
        )
    )


@router.get(
    "/{id_secao}",
    response_model=SecaoCardapioResponse,
)
def buscar_secao(
    id_restaurante: int,
    id_cardapio: int,
    id_secao: int,
    db: Session = Depends(get_db),
):
    return (
        secao_cardapio_controller
        .buscar_secao(
            db,
            id_restaurante,
            id_cardapio,
            id_secao,
        )
    )


@router.patch(
    "/{id_secao}",
    response_model=SecaoCardapioResponse,
)
def atualizar_secao(
    id_restaurante: int,
    id_cardapio: int,
    id_secao: int,
    dados: SecaoCardapioUpdate,
    db: Session = Depends(get_db),
):
    return (
        secao_cardapio_controller
        .atualizar_secao(
            db,
            id_restaurante,
            id_cardapio,
            id_secao,
            dados,
        )
    )


@router.delete(
    "/{id_secao}",
)
def deletar_secao(
    id_restaurante: int,
    id_cardapio: int,
    id_secao: int,
    db: Session = Depends(get_db),
):
    return (
        secao_cardapio_controller
        .deletar_secao(
            db,
            id_restaurante,
            id_cardapio,
            id_secao,
        )
    )
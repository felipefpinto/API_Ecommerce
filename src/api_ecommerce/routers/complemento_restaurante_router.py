from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api_ecommerce.controllers import (
    complemento_controller,
)
from api_ecommerce.database.connection import get_db
from api_ecommerce.schemas.complemento_schema import (
    ComplementoCreate,
    ComplementoResponse,
    ComplementoUpdate,
)


router = APIRouter(
    prefix=(
        "/restaurantes/{id_restaurante}"
        "/grupos-complementos/{id_grupo}"
        "/complementos"
    ),
    tags=["Complementos do Restaurante"],
)


@router.post(
    "/",
    response_model=ComplementoResponse,
)
def criar_complemento_restaurante(
    id_restaurante: int,
    id_grupo: int,
    dados: ComplementoCreate,
    db: Session = Depends(get_db),
):
    return (
        complemento_controller
        .criar_complemento_restaurante(
            db,
            id_restaurante,
            id_grupo,
            dados,
        )
    )


@router.get(
    "/",
    response_model=list[ComplementoResponse],
)
def listar_complementos_restaurante(
    id_restaurante: int,
    id_grupo: int,
    db: Session = Depends(get_db),
):
    return (
        complemento_controller
        .listar_complementos_restaurante(
            db,
            id_restaurante,
            id_grupo,
        )
    )


@router.get(
    "/{id_complemento}",
    response_model=ComplementoResponse,
)
def buscar_complemento_restaurante(
    id_restaurante: int,
    id_grupo: int,
    id_complemento: int,
    db: Session = Depends(get_db),
):
    return (
        complemento_controller
        .buscar_complemento_restaurante(
            db,
            id_restaurante,
            id_grupo,
            id_complemento,
        )
    )


@router.patch(
    "/{id_complemento}",
    response_model=ComplementoResponse,
)
def atualizar_complemento_restaurante(
    id_restaurante: int,
    id_grupo: int,
    id_complemento: int,
    dados: ComplementoUpdate,
    db: Session = Depends(get_db),
):
    return (
        complemento_controller
        .atualizar_complemento_restaurante(
            db,
            id_restaurante,
            id_grupo,
            id_complemento,
            dados,
        )
    )


@router.delete(
    "/{id_complemento}",
)
def deletar_complemento_restaurante(
    id_restaurante: int,
    id_grupo: int,
    id_complemento: int,
    db: Session = Depends(get_db),
):
    return (
        complemento_controller
        .deletar_complemento_restaurante(
            db,
            id_restaurante,
            id_grupo,
            id_complemento,
        )
    )
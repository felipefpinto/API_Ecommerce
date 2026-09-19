from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api_ecommerce.database import get_db

from api_ecommerce.schemas import (
    ResponsavelRestauranteCreate,
    ResponsavelRestauranteResponse,
    ResponsavelRestauranteUpdate,
)

from api_ecommerce.controllers import responsavel_restaurante_controller

from api_ecommerce.models.responsavel_restaurante import (
    ResponsavelRestaurante,
)

router = APIRouter(
    prefix="/responsavel-restaurante",
    tags=["Responsável Restaurante"]
)


@router.post(
    "/",
    response_model=ResponsavelRestauranteResponse
)
def criar_responsavel(
    responsavel: ResponsavelRestauranteCreate,
    db: Session = Depends(get_db)
):
    return responsavel_restaurante_controller.criar_responsavel(
        db,
        responsavel
    )


@router.get(
    "/",
    response_model=list[ResponsavelRestauranteResponse]
)
def listar_responsaveis(
    db: Session = Depends(get_db)
):
    return responsavel_restaurante_controller.listar_responsaveis(
        db
    )

@router.get("/telefone")
def buscar_telefone(
    email: str,
    db: Session = Depends(get_db),
):
    responsavel = (
        db.query(ResponsavelRestaurante)
        .filter(
            ResponsavelRestaurante.email == email
        )
        .first()
    )

    if responsavel is None:
        raise HTTPException(
            status_code=404,
            detail="Responsável não encontrado",
        )

    numero_celular = str(
        responsavel.celular
    )

    celular_mascarado = (
        numero_celular[:2]
        + "*****"
        + numero_celular[-4:]
    )

    return {
        "numero": celular_mascarado
    }


@router.get("/email")
def buscar_email(
    celular: str,
    db: Session = Depends(get_db),
):
    responsavel = (
        db.query(ResponsavelRestaurante)
        .filter(
            ResponsavelRestaurante.celular
            == celular
        )
        .first()
    )

    if responsavel is None:
        raise HTTPException(
            status_code=404,
            detail="Responsável não encontrado",
        )

    email = responsavel.email

    partes_email = email.split("@")

    nome_usuario = partes_email[0]
    dominio = partes_email[1]

    nome_usuario_mascarado = (
        nome_usuario[:2]
        + "****"
        + nome_usuario[-2:]
    )

    email_mascarado = (
        nome_usuario_mascarado
        + "@"
        + dominio
    )

    return {
        "email": email_mascarado
    }



@router.get(
    "/{id_responsavel}",
    response_model=ResponsavelRestauranteResponse
)
def buscar_responsavel(
    id_responsavel: int,
    db: Session = Depends(get_db)
):
    return responsavel_restaurante_controller.buscar_responsavel(
        db,
        id_responsavel
    )


@router.get(
    "/email/{email}",
    response_model=ResponsavelRestauranteResponse
)
def buscar_responsavel_por_email(
    email: str,
    db: Session = Depends(get_db)
):
    return responsavel_restaurante_controller.buscar_responsavel_por_email(
        db,
        email
    )


@router.get(
    "/celular/{celular}",
    response_model=ResponsavelRestauranteResponse
)
def buscar_responsavel_por_celular(
    celular: str,
    db: Session = Depends(get_db)
):
    return responsavel_restaurante_controller.buscar_responsavel_por_celular(
        db,
        celular
    )

@router.get(
    "/{id_responsavel}",
    response_model=ResponsavelRestauranteResponse
)
def buscar_responsavel(
    id_responsavel: int,
    db: Session = Depends(get_db)
):
    return (
        responsavel_restaurante_controller
        .buscar_responsavel(
            db,
            id_responsavel
        )
    )


@router.put(
    "/{id_responsavel}",
    response_model=ResponsavelRestauranteResponse
)
def atualizar_responsavel(
    id_responsavel: int,
    responsavel_data: ResponsavelRestauranteUpdate,
    db: Session = Depends(get_db)
):
    return responsavel_restaurante_controller.atualizar_responsavel(
        db,
        id_responsavel,
        responsavel_data
    )


@router.patch(
    "/{id_responsavel}",
    response_model=ResponsavelRestauranteResponse
)
def atualizar_responsavel_parcial(
    id_responsavel: int,
    responsavel_data: ResponsavelRestauranteUpdate,
    db: Session = Depends(get_db)
):
    return responsavel_restaurante_controller.atualizar_responsavel(
        db,
        id_responsavel,
        responsavel_data
    )


@router.delete(
    "/{id_responsavel}"
)
def deletar_responsavel(
    id_responsavel: int,
    db: Session = Depends(get_db)
):
    return responsavel_restaurante_controller.deletar_responsavel(
        db,
        id_responsavel
    )


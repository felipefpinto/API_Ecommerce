from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.orm import Session

from api_ecommerce.controllers import (
    endereco_restaurante_controller,
)
from api_ecommerce.database import get_db
from api_ecommerce.schemas import (
    EnderecoRestauranteCreate,
    EnderecoRestauranteResponse,
    EnderecoRestauranteUpdate,
)


router = APIRouter(
    prefix="/restaurantes/{id_restaurante}/endereco",
    tags=["Endereco Restaurante"],
)


@router.post(
    "/",
    response_model=EnderecoRestauranteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def criar_endereco_restaurante(
    id_restaurante: int,
    endereco_data: EnderecoRestauranteCreate,
    db: Session = Depends(get_db),
):
    return await endereco_restaurante_controller.criar_endereco_restaurante(
        db,
        id_restaurante,
        endereco_data,
    )


@router.get(
    "/",
    response_model=EnderecoRestauranteResponse,
)
def buscar_endereco_restaurante(
    id_restaurante: int,
    db: Session = Depends(get_db),
):
    return endereco_restaurante_controller.buscar_endereco_restaurante(
        db,
        id_restaurante,
    )


@router.patch(
    "/",
    response_model=EnderecoRestauranteResponse,
)
async def atualizar_endereco_restaurante(
    id_restaurante: int,
    endereco_data: EnderecoRestauranteUpdate,
    db: Session = Depends(get_db),
):
    return await endereco_restaurante_controller.atualizar_endereco_restaurante(
        db,
        id_restaurante,
        endereco_data,
    )


@router.delete("/")
def deletar_endereco_restaurante(
    id_restaurante: int,
    db: Session = Depends(get_db),
):
    return endereco_restaurante_controller.deletar_endereco_restaurante(
        db,
        id_restaurante,
    )
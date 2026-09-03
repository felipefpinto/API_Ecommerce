from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api_ecommerce.controllers import endereco_controller
from api_ecommerce.database import get_db
from api_ecommerce.schemas import EnderecoCreate, EnderecoResponse, EnderecoUpdate


router = APIRouter(
    prefix="/usuario/{id_usuario}/enderecos",
    tags=["Enderecos"],
)


@router.post(
    "/",
    response_model=EnderecoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def criar_endereco(
    id_usuario: int,
    endereco_data: EnderecoCreate,
    db: Session = Depends(get_db),
):
    return await endereco_controller.criar_endereco(
        db,
        id_usuario,
        endereco_data,
    )


@router.get("/", response_model=list[EnderecoResponse])
def listar_enderecos_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
):
    return endereco_controller.listar_enderecos_usuario(db, id_usuario)


@router.get("/{id_endereco}", response_model=EnderecoResponse)
def buscar_endereco_usuario(
    id_usuario: int,
    id_endereco: int,
    db: Session = Depends(get_db),
):
    return endereco_controller.buscar_endereco_usuario(db, id_usuario, id_endereco)


@router.patch("/{id_endereco}", response_model=EnderecoResponse)
def atualizar_endereco(
    id_usuario: int,
    id_endereco: int,
    endereco_data: EnderecoUpdate,
    db: Session = Depends(get_db),
):
    return endereco_controller.atualizar_endereco(
        db,
        id_usuario,
        id_endereco,
        endereco_data,
    )

@router.patch(
    "{id_endereco}/principal",
    response_model=EnderecoResponse,
)
def definir_endereco_principal(
    id_usuario: int,
    id_endereco: int,
    db: Session = Depends(get_db),
):

    return endereco_controller.definir_endereco_principal(
        db,
        id_usuario,
        id_endereco,
    )

@router.delete("/{id_endereco}")
def deletar_endereco(
    id_usuario: int,
    id_endereco: int,
    db: Session = Depends(get_db),
):
    return endereco_controller.deletar_endereco(db, id_usuario, id_endereco)

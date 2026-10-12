from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile
)
from sqlalchemy.orm import Session

from api_ecommerce.controllers import (
    produto_controller,
)
from api_ecommerce.database.connection import (
    get_db,
)
from api_ecommerce.schemas.produto_schema import (
    ProdutoCreate,
    ProdutoResponse,
    ProdutoUpdate,
)


router = APIRouter(
    prefix="/restaurantes/{id_restaurante}/produtos",
    tags=["Produtos"],
)


@router.post(
    "/",
    response_model=ProdutoResponse,
)
def criar_produto(
    id_restaurante: int,
    dados: ProdutoCreate,
    db: Session = Depends(get_db),
):
    return produto_controller.criar_produto(
        db,
        id_restaurante,
        dados,
    )

@router.post(
    "/{id_produto}/imagem",
    response_model=ProdutoResponse,
)
async def upload_imagem_produto(
    id_restaurante: int,
    id_produto: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await produto_controller.upload_imagem_produto(
        db,
        id_restaurante,
        id_produto,
        arquivo,
    )


@router.get(
    "/",
    response_model=list[ProdutoResponse],
)
def listar_produtos(
    id_restaurante: int,
    db: Session = Depends(get_db),
):
    return produto_controller.listar_produtos(
        db,
        id_restaurante,
    )


@router.get(
    "/{id_produto}",
    response_model=ProdutoResponse,
)
def buscar_produto(
    id_restaurante: int,
    id_produto: int,
    db: Session = Depends(get_db),
):
    return produto_controller.buscar_produto(
        db,
        id_restaurante,
        id_produto,
    )


@router.patch(
    "/{id_produto}",
    response_model=ProdutoResponse,
)
def atualizar_produto(
    id_restaurante: int,
    id_produto: int,
    dados: ProdutoUpdate,
    db: Session = Depends(get_db),
):
    return produto_controller.atualizar_produto(
        db,
        id_restaurante,
        id_produto,
        dados,
    )


@router.delete(
    "/{id_produto}",
)
def deletar_produto(
    id_restaurante: int,
    id_produto: int,
    db: Session = Depends(get_db),
):
    return produto_controller.deletar_produto(
        db,
        id_restaurante,
        id_produto,
    )
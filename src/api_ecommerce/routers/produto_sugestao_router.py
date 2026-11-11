from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api_ecommerce.controllers import produto_sugestao_controller

from api_ecommerce.database.connection import (
    get_db,
)

from api_ecommerce.schemas.produto_sugestao import (
    ProdutoSugestaoCreate,
    ProdutoSugestaoResponse,
    ProdutoSugestaoUpdate,
)


router = APIRouter(
    prefix="/restaurantes/{id_restaurante}/produtos/{id_produto}/sugestoes",
    tags=["Compre também"],
)


@router.post(
    "/",
    response_model=ProdutoSugestaoResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_sugestao(
    id_restaurante: int,
    id_produto: int,
    dados: ProdutoSugestaoCreate,
    db: Session = Depends(get_db),
):
    return produto_sugestao_controller.criar_sugestao(
        db,
        id_restaurante,
        id_produto,
        dados,
    )

@router.get(
    "/",
    response_model=list[ProdutoSugestaoResponse],
)
def listar_sugestoes(
    id_restaurante: int,
    id_produto: int,
    db: Session = Depends(get_db),
):
    return produto_sugestao_controller.listar_sugestoes(
        db,
        id_restaurante,
        id_produto,
    )

@router.patch(
    "/{id_sugestao}",
    response_model=ProdutoSugestaoResponse,
)
def atualizar_sugestao(
    id_restaurante: int,
    id_produto: int,
    id_sugestao: int,
    dados: ProdutoSugestaoUpdate,
    db: Session = Depends(get_db),
):
    return produto_sugestao_controller.atualizar_sugestao(
        db,
        id_restaurante,
        id_produto,
        id_sugestao,
        dados,
    )


@router.delete(
    "/{id_sugestao}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deletar_sugestao(
    id_restaurante: int,
    id_produto: int,
    id_sugestao: int,
    db: Session = Depends(get_db),
):
    produto_sugestao_controller.deletar_sugestao(
        db,
        id_restaurante,
        id_produto,
        id_sugestao,
    )
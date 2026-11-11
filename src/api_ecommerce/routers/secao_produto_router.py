from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from api_ecommerce.controllers import (
    secao_produto_controller,
)
from api_ecommerce.database.connection import (
    get_db,
)
from api_ecommerce.schemas.secao_produto_schema import (
    SecaoProdutoCreate,
    SecaoProdutoResponse,
    SecaoProdutoUpdate,
)


router = APIRouter(
    prefix="/secoes/{id_secao}/produtos",
    tags=["Produtos da Seção"],
)


@router.post(
    "/",
    response_model=SecaoProdutoResponse,
)
def adicionar_produto_secao(
    id_secao: int,
    dados: SecaoProdutoCreate,
    db: Session = Depends(get_db),
):
    return (
        secao_produto_controller
        .adicionar_produto_secao(
            db,
            id_secao,
            dados,
        )
    )


@router.get(
    "/",
    response_model=list[
        SecaoProdutoResponse
    ],
)
def listar_produtos_secao(
    id_secao: int,
    db: Session = Depends(get_db),
):
    return (
        secao_produto_controller
        .listar_produtos_secao(
            db,
            id_secao,
        )
    )


@router.patch(
    "/{id_produto}",
    response_model=SecaoProdutoResponse,
)
def atualizar_produto_secao(
    id_secao: int,
    id_produto: int,
    dados: SecaoProdutoUpdate,
    db: Session = Depends(get_db),
):
    return (
        secao_produto_controller
        .atualizar_produto_secao(
            db,
            id_secao,
            id_produto,
            dados,
        )
    )


@router.delete(
    "/{id_produto}",
)
def remover_produto_secao(
    id_secao: int,
    id_produto: int,
    db: Session = Depends(get_db),
):
    return (
        secao_produto_controller
        .remover_produto_secao(
            db,
            id_secao,
            id_produto,
        )
    )
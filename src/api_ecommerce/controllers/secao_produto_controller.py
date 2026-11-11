from fastapi import HTTPException
from sqlalchemy.orm import Session

from api_ecommerce.models.produto import Produto
from api_ecommerce.models.secao_cardapio import (
    SecaoCardapio,
)
from api_ecommerce.models.secao_produto import (
    SecaoProduto,
)
from api_ecommerce.schemas.secao_produto_schema import (
    SecaoProdutoCreate,
    SecaoProdutoUpdate,
)
from api_ecommerce.models.cardapio import (
    Cardapio,
)


def adicionar_produto_secao(
    db: Session,
    id_secao: int,
    dados: SecaoProdutoCreate,
):
    secao = (
        db.query(SecaoCardapio)
        .filter(
            SecaoCardapio.id_secao
            == id_secao
        )
        .first()
    )

    if secao is None:
        raise HTTPException(
            status_code=404,
            detail="Seção não encontrada.",
        )

    produto = (
        db.query(Produto)
        .filter(
            Produto.id_produto
            == dados.id_produto
        )
        .first()
    )

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado.",
        )

    cardapio = (
        db.query(Cardapio)
        .filter(
            Cardapio.id_cardapio
            == secao.id_cardapio
        )
        .first()
    )

    if cardapio is None:
        raise HTTPException(
            status_code=404,
            detail="Cardápio não encontrado.",
        )

    if (
        produto.id_restaurante
        != cardapio.id_restaurante
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "O produto não pertence "
                "ao mesmo restaurante da seção."
            ),
        )

    existente = (
        db.query(SecaoProduto)
        .filter(
            SecaoProduto.id_secao
            == id_secao,
            SecaoProduto.id_produto
            == dados.id_produto,
        )
        .first()
    )

    if existente:
        raise HTTPException(
            status_code=400,
            detail=(
                "Este produto já pertence "
                "a esta seção."
            ),
        )

    relacao = SecaoProduto(
        id_secao=id_secao,
        id_produto=dados.id_produto,
        preco=dados.preco,
        ordem=dados.ordem,
    )

    db.add(relacao)
    db.commit()
    db.refresh(relacao)

    return relacao


def listar_produtos_secao(
    db: Session,
    id_secao: int,
):
    return (
        db.query(SecaoProduto)
        .filter(
            SecaoProduto.id_secao
            == id_secao
        )
        .order_by(
            SecaoProduto.ordem,
            SecaoProduto.id,
        )
        .all()
    )


def atualizar_produto_secao(
    db: Session,
    id_secao: int,
    id_produto: int,
    dados: SecaoProdutoUpdate,
):
    relacao = (
        db.query(SecaoProduto)
        .filter(
            SecaoProduto.id_secao
            == id_secao,
            SecaoProduto.id_produto
            == id_produto,
        )
        .first()
    )

    if relacao is None:
        raise HTTPException(
            status_code=404,
            detail="Relação não encontrada.",
        )

    dados_update = (
        dados.model_dump(
            exclude_unset=True
        )
    )

    for campo, valor in (
        dados_update.items()
    ):
        setattr(
            relacao,
            campo,
            valor,
        )

    db.commit()
    db.refresh(relacao)

    return relacao

def remover_produto_secao(
    db: Session,
    id_secao: int,
    id_produto: int,
):
    relacao = (
        db.query(SecaoProduto)
        .filter(
            SecaoProduto.id_secao
            == id_secao,
            SecaoProduto.id_produto
            == id_produto,
        )
        .first()
    )

    if relacao is None:
        raise HTTPException(
            status_code=404,
            detail="Relação não encontrada.",
        )

    db.delete(relacao)
    db.commit()

    return {
        "message":
            "Produto removido da seção com sucesso."
    }
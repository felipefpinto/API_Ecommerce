from fastapi import HTTPException
from sqlalchemy.orm import Session

from api_ecommerce.models.produto import Produto
from api_ecommerce.models.produto_sugestao import ProdutoSugestao
from api_ecommerce.schemas.produto_sugestao import ProdutoSugestaoCreate, ProdutoSugestaoUpdate


def criar_sugestao(
    db: Session,
    id_restaurante: int,
    id_produto: int,
    dados: ProdutoSugestaoCreate,
):
    produto = (
        db.query(Produto)
        .filter(
            Produto.id_produto == id_produto,
            Produto.id_restaurante == id_restaurante,
        )
        .first()
    )

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado neste restaurante.",
        )

    produto_sugerido = (
        db.query(Produto)
        .filter(
            Produto.id_produto == dados.id_produto_sugerido,
            Produto.id_restaurante == id_restaurante,
        )
        .first()
    )

    if not produto_sugerido:
        raise HTTPException(
            status_code=404,
            detail="Produto sugerido não encontrado neste restaurante.",
        )

    if id_produto == dados.id_produto_sugerido:
        raise HTTPException(
            status_code=400,
            detail="Um produto não pode ser sugerido para ele mesmo.",
        )

    sugestao_existente = (
        db.query(ProdutoSugestao)
        .filter(
            ProdutoSugestao.id_produto == id_produto,
            ProdutoSugestao.id_produto_sugerido
            == dados.id_produto_sugerido,
        )
        .first()
    )

    if sugestao_existente:
        raise HTTPException(
            status_code=409,
            detail="Este produto já está em 'Compre também'.",
        )

    sugestao = ProdutoSugestao(
        id_produto=id_produto,
        id_produto_sugerido=dados.id_produto_sugerido,
        ordem=dados.ordem,
        ativo=True,
    )

    db.add(sugestao)
    db.commit()
    db.refresh(sugestao)

    return sugestao

def listar_sugestoes(
    db: Session,
    id_restaurante: int,
    id_produto: int,
):
    produto = (
        db.query(Produto)
        .filter(
            Produto.id_produto == id_produto,
            Produto.id_restaurante == id_restaurante,
        )
        .first()
    )

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado neste restaurante.",
        )

    sugestoes = (
        db.query(ProdutoSugestao)
        .join(
            Produto,
            Produto.id_produto
            == ProdutoSugestao.id_produto_sugerido,
        )
        .filter(
            ProdutoSugestao.id_produto == id_produto,
            Produto.id_restaurante == id_restaurante,
        )
        .order_by(
            ProdutoSugestao.ordem,
            ProdutoSugestao.id,
        )
        .all()
    )

    return sugestoes    

def atualizar_sugestao(
    db: Session,
    id_restaurante: int,
    id_produto: int,
    id_sugestao: int,
    dados: ProdutoSugestaoUpdate,
):
    sugestao = (
        db.query(ProdutoSugestao)
        .join(
            Produto,
            Produto.id_produto == ProdutoSugestao.id_produto,
        )
        .filter(
            ProdutoSugestao.id == id_sugestao,
            ProdutoSugestao.id_produto == id_produto,
            Produto.id_restaurante == id_restaurante,
        )
        .first()
    )

    if not sugestao:
        raise HTTPException(
            status_code=404,
            detail="Sugestão não encontrada.",
        )

    dados_update = dados.model_dump(
        exclude_unset=True
    )

    for campo, valor in dados_update.items():
        setattr(sugestao, campo, valor)

    db.commit()
    db.refresh(sugestao)

    return sugestao


def deletar_sugestao(
    db: Session,
    id_restaurante: int,
    id_produto: int,
    id_sugestao: int,
):
    sugestao = (
        db.query(ProdutoSugestao)
        .join(
            Produto,
            Produto.id_produto == ProdutoSugestao.id_produto,
        )
        .filter(
            ProdutoSugestao.id == id_sugestao,
            ProdutoSugestao.id_produto == id_produto,
            Produto.id_restaurante == id_restaurante,
        )
        .first()
    )

    if not sugestao:
        raise HTTPException(
            status_code=404,
            detail="Sugestão não encontrada.",
        )

    db.delete(sugestao)
    db.commit()
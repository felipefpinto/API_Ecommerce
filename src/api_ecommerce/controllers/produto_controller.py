from fastapi import HTTPException,UploadFile
from sqlalchemy.orm import Session
from pathlib import Path

from api_ecommerce.models.produto import Produto
from api_ecommerce.models.restaurante import Restaurante
from api_ecommerce.schemas.produto_schema import (
    ProdutoCreate,
    ProdutoUpdate,
)

UPLOAD_DIR = Path(
    "uploads/restaurantes/produtos"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)



def criar_produto(
    db: Session,
    id_restaurante: int,
    dados: ProdutoCreate,
):
    restaurante = (
        db.query(Restaurante)
        .filter(
            Restaurante.id_restaurante
            == id_restaurante
        )
        .first()
    )

    if restaurante is None:
        raise HTTPException(
            status_code=404,
            detail="Restaurante não encontrado.",
        )

    produto = Produto(
        id_restaurante=id_restaurante,
        nome=dados.nome.strip(),
        descricao=(
            dados.descricao.strip()
            if dados.descricao
            else None
        ),
        preco_base=dados.preco_base,
        estoque=dados.estoque,
        serve_pessoas=dados.serve_pessoas,
    )

    db.add(produto)
    db.commit()
    db.refresh(produto)

    return produto

async def upload_imagem_produto(
    db: Session,
    id_restaurante: int,
    id_produto: int,
    arquivo: UploadFile,
):
    produto = buscar_produto(
        db,
        id_restaurante,
        id_produto,
    )

    tipos_permitidos = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }

    if (
        arquivo.content_type
        not in tipos_permitidos
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Formato de imagem inválido. "
                "Use JPG, PNG ou WEBP."
            ),
        )

    conteudo = await arquivo.read()

    tamanho_maximo = (
        5 * 1024 * 1024
    )

    if len(conteudo) > tamanho_maximo:
        raise HTTPException(
            status_code=400,
            detail=(
                "A imagem deve ter no "
                "máximo 5 MB."
            ),
        )

    # Remove imagem anterior
    if produto.imagem_url:
        caminho_antigo = Path(
            produto.imagem_url.lstrip("/")
        )

        if caminho_antigo.exists():
            caminho_antigo.unlink()

    extensao = tipos_permitidos[
        arquivo.content_type
    ]

    nome_arquivo = (
        f"produto_{id_produto}"
        f"{extensao}"
    )

    caminho_arquivo = (
        UPLOAD_DIR /
        nome_arquivo
    )

    caminho_arquivo.write_bytes(
        conteudo
    )

    produto.imagem_url = (
        "/uploads/restaurantes/"
        f"produtos/{nome_arquivo}"
    )

    db.commit()
    db.refresh(produto)

    return produto

def listar_produtos(
    db: Session,
    id_restaurante: int,
):
    return (
        db.query(Produto)
        .filter(
            Produto.id_restaurante
            == id_restaurante
        )
        .order_by(
            Produto.nome
        )
        .all()
    )


def buscar_produto(
    db: Session,
    id_restaurante: int,
    id_produto: int,
):
    produto = (
        db.query(Produto)
        .filter(
            Produto.id_produto
            == id_produto,
            Produto.id_restaurante
            == id_restaurante,
        )
        .first()
    )

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado.",
        )

    return produto


def atualizar_produto(
    db: Session,
    id_restaurante: int,
    id_produto: int,
    dados: ProdutoUpdate,
):
    produto = buscar_produto(
        db,
        id_restaurante,
        id_produto,
    )

    dados_update = dados.model_dump(
        exclude_unset=True
    )

    if "nome" in dados_update:
        dados_update["nome"] = (
            dados_update["nome"].strip()
        )

    if (
        "descricao" in dados_update
        and dados_update["descricao"]
    ):
        dados_update["descricao"] = (
            dados_update["descricao"].strip()
        )

    for campo, valor in dados_update.items():
        setattr(
            produto,
            campo,
            valor,
        )

    db.commit()
    db.refresh(produto)

    return produto


def deletar_produto(
    db: Session,
    id_restaurante: int,
    id_produto: int,
):
    produto = buscar_produto(
        db,
        id_restaurante,
        id_produto,
    )

    caminho_imagem = None

    if produto.imagem_url:
        caminho_imagem = Path(
            produto.imagem_url.lstrip("/")
        )

    try:
        db.delete(produto)
        db.commit()

        if (
            caminho_imagem
            and caminho_imagem.exists()
        ):
            caminho_imagem.unlink()

        return {
            "message":
                "Produto excluído com sucesso."
        }

    except Exception:
        db.rollback()
        raise
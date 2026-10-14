from fastapi import HTTPException
from sqlalchemy.orm import Session

from api_ecommerce.models.complemento import Complemento
from api_ecommerce.models.grupo_complemento import GrupoComplemento
from api_ecommerce.models.produto import Produto
from api_ecommerce.models.produto_grupo_complemento import (
    ProdutoGrupoComplemento,
)
from api_ecommerce.schemas.complemento_schema import (
    ComplementoCreate,
    ComplementoUpdate,
)








def buscar_grupo(
    db: Session,
    id_restaurante: int,
    id_produto: int,
    id_grupo: int,
):
    grupo = (
        db.query(GrupoComplemento)
        .join(
            ProdutoGrupoComplemento,
            ProdutoGrupoComplemento.id_grupo
            == GrupoComplemento.id_grupo,
        )
        .join(
            Produto,
            Produto.id_produto
            == ProdutoGrupoComplemento.id_produto,
        )
        .filter(
            GrupoComplemento.id_grupo
            == id_grupo,
            GrupoComplemento.id_restaurante
            == id_restaurante,
            Produto.id_produto
            == id_produto,
            Produto.id_restaurante
            == id_restaurante,
        )
        .first()
    )

    if grupo is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Grupo de complementos não "
                "encontrado para este produto."
            ),
        )

    return grupo


def buscar_grupo_restaurante(
    db: Session,
    id_restaurante: int,
    id_grupo: int,
):
    grupo = (
        db.query(GrupoComplemento)
        .filter(
            GrupoComplemento.id_grupo == id_grupo,
            GrupoComplemento.id_restaurante == id_restaurante,
        )
        .first()
    )

    if grupo is None:
        raise HTTPException(
            status_code=404,
            detail="Grupo de complementos não encontrado.",
        )

    return grupo

def criar_complemento(
    db: Session,
    id_restaurante: int,
    id_produto: int,
    id_grupo: int,
    dados: ComplementoCreate,
):
    buscar_grupo(
        db,
        id_restaurante,
        id_produto,
        id_grupo,
    )

    complemento = Complemento(
        id_grupo=id_grupo,
        nome=dados.nome.strip(),
        descricao=(
            dados.descricao.strip()
            if dados.descricao
            else None
        ),
        preco_adicional=dados.preco_adicional,
        estoque=dados.estoque,
        ordem=dados.ordem,
    )

    db.add(complemento)
    db.commit()
    db.refresh(complemento)

    return complemento


def listar_complementos(
    db: Session,
    id_restaurante: int,
    id_produto: int,
    id_grupo: int,
):
    buscar_grupo(
        db,
        id_restaurante,
        id_produto,
        id_grupo,
    )

    return (
        db.query(Complemento)
        .filter(
            Complemento.id_grupo == id_grupo
        )
        .order_by(
            Complemento.ordem,
            Complemento.nome,
        )
        .all()
    )


def buscar_complemento(
    db: Session,
    id_restaurante: int,
    id_produto: int,
    id_grupo: int,
    id_complemento: int,
):
    buscar_grupo(
        db,
        id_restaurante,
        id_produto,
        id_grupo,
    )

    complemento = (
        db.query(Complemento)
        .filter(
            Complemento.id_complemento
            == id_complemento,
            Complemento.id_grupo
            == id_grupo,
        )
        .first()
    )

    if complemento is None:
        raise HTTPException(
            status_code=404,
            detail="Complemento não encontrado.",
        )

    return complemento


def atualizar_complemento(
    db: Session,
    id_restaurante: int,
    id_produto: int,
    id_grupo: int,
    id_complemento: int,
    dados: ComplementoUpdate,
):
    complemento = buscar_complemento(
        db,
        id_restaurante,
        id_produto,
        id_grupo,
        id_complemento,
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
            complemento,
            campo,
            valor,
        )

    db.commit()
    db.refresh(complemento)

    return complemento


def deletar_complemento(
    db: Session,
    id_restaurante: int,
    id_produto: int,
    id_grupo: int,
    id_complemento: int,
):
    complemento = buscar_complemento(
        db,
        id_restaurante,
        id_produto,
        id_grupo,
        id_complemento,
    )

    try:
        db.delete(complemento)
        db.commit()

        return {
            "message": (
                "Complemento excluído com sucesso."
            )
        }

    except Exception:
        db.rollback()
        raise

def criar_complemento_restaurante(
    db: Session,
    id_restaurante: int,
    id_grupo: int,
    dados: ComplementoCreate,
):
    buscar_grupo_restaurante(
        db,
        id_restaurante,
        id_grupo,
    )

    complemento = Complemento(
        id_grupo=id_grupo,
        nome=dados.nome.strip(),
        descricao=(
            dados.descricao.strip()
            if dados.descricao
            else None
        ),
        preco_adicional=dados.preco_adicional,
        estoque=dados.estoque,
        ordem=dados.ordem,
    )

    db.add(complemento)
    db.commit()
    db.refresh(complemento)

    return complemento


def listar_complementos_restaurante(
    db: Session,
    id_restaurante: int,
    id_grupo: int,
):
    buscar_grupo_restaurante(
        db,
        id_restaurante,
        id_grupo,
    )

    return (
        db.query(Complemento)
        .filter(
            Complemento.id_grupo == id_grupo
        )
        .order_by(
            Complemento.ordem,
            Complemento.nome,
        )
        .all()
    )


def buscar_complemento_restaurante(
    db: Session,
    id_restaurante: int,
    id_grupo: int,
    id_complemento: int,
):
    buscar_grupo_restaurante(
        db,
        id_restaurante,
        id_grupo,
    )

    complemento = (
        db.query(Complemento)
        .filter(
            Complemento.id_complemento
            == id_complemento,
            Complemento.id_grupo
            == id_grupo,
        )
        .first()
    )

    if complemento is None:
        raise HTTPException(
            status_code=404,
            detail="Complemento não encontrado.",
        )

    return complemento


def atualizar_complemento_restaurante(
    db: Session,
    id_restaurante: int,
    id_grupo: int,
    id_complemento: int,
    dados: ComplementoUpdate,
):
    complemento = buscar_complemento_restaurante(
        db,
        id_restaurante,
        id_grupo,
        id_complemento,
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
            complemento,
            campo,
            valor,
        )

    db.commit()
    db.refresh(complemento)

    return complemento


def deletar_complemento_restaurante(
    db: Session,
    id_restaurante: int,
    id_grupo: int,
    id_complemento: int,
):
    complemento = buscar_complemento_restaurante(
        db,
        id_restaurante,
        id_grupo,
        id_complemento,
    )

    try:
        db.delete(complemento)
        db.commit()

        return {
            "message": (
                "Complemento excluído com sucesso."
            )
        }

    except Exception:
        db.rollback()
        raise
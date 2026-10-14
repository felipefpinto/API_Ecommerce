from fastapi import HTTPException
from sqlalchemy.orm import Session

from api_ecommerce.models.grupo_complemento import (
    GrupoComplemento,
)
from api_ecommerce.models.produto import Produto
from api_ecommerce.models.produto_grupo_complemento import (
    ProdutoGrupoComplemento,
)
from api_ecommerce.models.restaurante import Restaurante
from api_ecommerce.schemas.grupo_complemento_schema import (
    GrupoComplementoCreate,
    GrupoComplementoUpdate,
)


def buscar_restaurante(
    db: Session,
    id_restaurante: int,
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

    return restaurante


def buscar_produto(
    db: Session,
    id_restaurante: int,
    id_produto: int,
):
    produto = (
        db.query(Produto)
        .filter(
            Produto.id_produto == id_produto,
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


def buscar_grupo_do_restaurante(
    db: Session,
    id_restaurante: int,
    id_grupo: int,
):
    grupo = (
        db.query(GrupoComplemento)
        .filter(
            GrupoComplemento.id_grupo
            == id_grupo,
            GrupoComplemento.id_restaurante
            == id_restaurante,
        )
        .first()
    )

    if grupo is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Grupo de complementos "
                "não encontrado."
            ),
        )

    return grupo


def criar_grupo_complemento(
    db: Session,
    id_restaurante: int,
    id_produto: int,
    dados: GrupoComplementoCreate,
):
    buscar_produto(
        db,
        id_restaurante,
        id_produto,
    )

    grupo = GrupoComplemento(
        id_restaurante=id_restaurante,
        nome=dados.nome.strip(),
        descricao=(
            dados.descricao.strip()
            if dados.descricao
            else None
        ),
        obrigatorio=dados.obrigatorio,
        min_selecoes=dados.min_selecoes,
        max_selecoes=dados.max_selecoes,
        ordem=dados.ordem,
    )

    try:
        db.add(grupo)
        db.flush()

        associacao = ProdutoGrupoComplemento(
            id_produto=id_produto,
            id_grupo=grupo.id_grupo,
        )

        db.add(associacao)

        db.commit()
        db.refresh(grupo)

        return grupo

    except Exception:
        db.rollback()
        raise


def listar_grupos_complemento(
    db: Session,
    id_restaurante: int,
    id_produto: int,
):
    buscar_produto(
        db,
        id_restaurante,
        id_produto,
    )

    return (
        db.query(GrupoComplemento)
        .join(
            ProdutoGrupoComplemento,
            ProdutoGrupoComplemento.id_grupo
            == GrupoComplemento.id_grupo,
        )
        .filter(
            ProdutoGrupoComplemento.id_produto
            == id_produto,
            GrupoComplemento.id_restaurante
            == id_restaurante,
        )
        .order_by(
            GrupoComplemento.ordem,
            GrupoComplemento.nome,
        )
        .all()
    )


def buscar_grupo_complemento(
    db: Session,
    id_restaurante: int,
    id_produto: int,
    id_grupo: int,
):
    buscar_produto(
        db,
        id_restaurante,
        id_produto,
    )

    grupo = (
        db.query(GrupoComplemento)
        .join(
            ProdutoGrupoComplemento,
            ProdutoGrupoComplemento.id_grupo
            == GrupoComplemento.id_grupo,
        )
        .filter(
            GrupoComplemento.id_grupo
            == id_grupo,
            GrupoComplemento.id_restaurante
            == id_restaurante,
            ProdutoGrupoComplemento.id_produto
            == id_produto,
        )
        .first()
    )

    if grupo is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Grupo de complementos não está "
                "associado a este produto."
            ),
        )

    return grupo

def listar_grupos_restaurante(
    db: Session,
    id_restaurante: int,
):
    buscar_restaurante(
        db,
        id_restaurante,
    )

    return (
        db.query(GrupoComplemento)
        .filter(
            GrupoComplemento.id_restaurante
            == id_restaurante
        )
        .order_by(
            GrupoComplemento.ordem,
            GrupoComplemento.nome,
        )
        .all()
    )   

def associar_grupo_produto(
    db: Session,
    id_restaurante: int,
    id_produto: int,
    id_grupo: int,
):
    buscar_produto(
        db,
        id_restaurante,
        id_produto,
    )

    grupo = buscar_grupo_do_restaurante(
        db,
        id_restaurante,
        id_grupo,
    )

    associacao_existente = (
        db.query(ProdutoGrupoComplemento)
        .filter(
            ProdutoGrupoComplemento.id_produto
            == id_produto,
            ProdutoGrupoComplemento.id_grupo
            == id_grupo,
        )
        .first()
    )

    if associacao_existente:
        raise HTTPException(
            status_code=409,
            detail=(
                "Este grupo já está associado "
                "ao produto."
            ),
        )

    associacao = ProdutoGrupoComplemento(
        id_produto=id_produto,
        id_grupo=id_grupo,
    )

    db.add(associacao)
    db.commit()

    return grupo

def desassociar_grupo_produto(
    db: Session,
    id_restaurante: int,
    id_produto: int,
    id_grupo: int,
):
    buscar_produto(
        db,
        id_restaurante,
        id_produto,
    )

    buscar_grupo_do_restaurante(
        db,
        id_restaurante,
        id_grupo,
    )

    associacao = (
        db.query(ProdutoGrupoComplemento)
        .filter(
            ProdutoGrupoComplemento.id_produto
            == id_produto,
            ProdutoGrupoComplemento.id_grupo
            == id_grupo,
        )
        .first()
    )

    if associacao is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Este grupo não está associado "
                "ao produto."
            ),
        )

    db.delete(associacao)
    db.commit()

    return {
        "message": (
            "Grupo removido do produto "
            "com sucesso."
        )
    }

def atualizar_grupo_restaurante(
    db: Session,
    id_restaurante: int,
    id_grupo: int,
    dados: GrupoComplementoUpdate,
):
    grupo = buscar_grupo_do_restaurante(
        db,
        id_restaurante,
        id_grupo,
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

    obrigatorio = dados_update.get(
        "obrigatorio",
        grupo.obrigatorio,
    )

    min_selecoes = dados_update.get(
        "min_selecoes",
        grupo.min_selecoes,
    )

    max_selecoes = dados_update.get(
        "max_selecoes",
        grupo.max_selecoes,
    )

    if min_selecoes > max_selecoes:
        raise HTTPException(
            status_code=400,
            detail=(
                "min_selecoes não pode ser maior "
                "que max_selecoes."
            ),
        )

    if obrigatorio and min_selecoes < 1:
        raise HTTPException(
            status_code=400,
            detail=(
                "Grupos obrigatórios devem possuir "
                "min_selecoes maior ou igual a 1."
            ),
        )

    for campo, valor in dados_update.items():
        setattr(
            grupo,
            campo,
            valor,
        )

    db.commit()
    db.refresh(grupo)

    return grupo


def atualizar_grupo_complemento(
    db: Session,
    id_restaurante: int,
    id_produto: int,
    id_grupo: int,
    dados: GrupoComplementoUpdate,
):
    grupo = buscar_grupo_complemento(
        db,
        id_restaurante,
        id_produto,
        id_grupo,
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

    obrigatorio = dados_update.get(
        "obrigatorio",
        grupo.obrigatorio,
    )

    min_selecoes = dados_update.get(
        "min_selecoes",
        grupo.min_selecoes,
    )

    max_selecoes = dados_update.get(
        "max_selecoes",
        grupo.max_selecoes,
    )

    if min_selecoes > max_selecoes:
        raise HTTPException(
            status_code=400,
            detail=(
                "min_selecoes não pode ser maior "
                "que max_selecoes."
            ),
        )

    if obrigatorio and min_selecoes < 1:
        raise HTTPException(
            status_code=400,
            detail=(
                "Grupos obrigatórios devem possuir "
                "min_selecoes maior ou igual a 1."
            ),
        )

    for campo, valor in dados_update.items():
        setattr(
            grupo,
            campo,
            valor,
        )

    db.commit()
    db.refresh(grupo)

    return grupo


def deletar_grupo_complemento(
    db: Session,
    id_restaurante: int,
    id_grupo: int,
):
    grupo = buscar_grupo_do_restaurante(
        db,
        id_restaurante,
        id_grupo,
    )

    try:
        db.delete(grupo)
        db.commit()

        return {
            "message": (
                "Grupo de complementos excluído "
                "com sucesso."
            )
        }

    except Exception:
        db.rollback()
        raise
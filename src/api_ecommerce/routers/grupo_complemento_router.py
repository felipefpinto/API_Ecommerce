from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from api_ecommerce.controllers import (
    grupo_complemento_controller,
)
from api_ecommerce.database.connection import (
    get_db,
)
from api_ecommerce.schemas.grupo_complemento_schema import (
    GrupoComplementoCreate,
    GrupoComplementoResponse,
    GrupoComplementoUpdate,
)


router = APIRouter(
    prefix="/restaurantes/{id_restaurante}",
    tags=["Grupos de Complementos"],
)


# =========================================================
# GRUPOS DO RESTAURANTE
# =========================================================


@router.get(
    "/grupos-complementos/",
    response_model=list[GrupoComplementoResponse],
)
def listar_grupos_restaurante(
    id_restaurante: int,
    db: Session = Depends(get_db),
):
    return (
        grupo_complemento_controller
        .listar_grupos_restaurante(
            db,
            id_restaurante,
        )
    )


# =========================================================
# GRUPOS DO PRODUTO
# =========================================================


@router.post(
    "/produtos/{id_produto}/grupos-complementos/",
    response_model=GrupoComplementoResponse,
)
def criar_grupo_complemento(
    id_restaurante: int,
    id_produto: int,
    dados: GrupoComplementoCreate,
    db: Session = Depends(get_db),
):
    return (
        grupo_complemento_controller
        .criar_grupo_complemento(
            db,
            id_restaurante,
            id_produto,
            dados,
        )
    )


@router.get(
    "/produtos/{id_produto}/grupos-complementos/",
    response_model=list[GrupoComplementoResponse],
)
def listar_grupos_complemento(
    id_restaurante: int,
    id_produto: int,
    db: Session = Depends(get_db),
):
    return (
        grupo_complemento_controller
        .listar_grupos_complemento(
            db,
            id_restaurante,
            id_produto,
        )
    )


@router.get(
    "/produtos/{id_produto}/grupos-complementos/{id_grupo}",
    response_model=GrupoComplementoResponse,
)
def buscar_grupo_complemento(
    id_restaurante: int,
    id_produto: int,
    id_grupo: int,
    db: Session = Depends(get_db),
):
    return (
        grupo_complemento_controller
        .buscar_grupo_complemento(
            db,
            id_restaurante,
            id_produto,
            id_grupo,
        )
    )

@router.get(
    "/grupos-complementos/{id_grupo}",
    response_model=GrupoComplementoResponse,
)
def buscar_grupo_restaurante(
    id_restaurante: int,
    id_grupo: int,
    db: Session = Depends(get_db),
):
    return (
        grupo_complemento_controller
        .buscar_grupo_do_restaurante(
            db,
            id_restaurante,
            id_grupo,
        )
    )


@router.patch(
    "/grupos-complementos/{id_grupo}",
    response_model=GrupoComplementoResponse,
)
def atualizar_grupo_restaurante(
    id_restaurante: int,
    id_grupo: int,
    dados: GrupoComplementoUpdate,
    db: Session = Depends(get_db),
):
    return (
        grupo_complemento_controller
        .atualizar_grupo_restaurante(
            db,
            id_restaurante,
            id_grupo,
            dados,
        )
    )


@router.patch(
    "/produtos/{id_produto}/grupos-complementos/{id_grupo}",
    response_model=GrupoComplementoResponse,
)
def atualizar_grupo_complemento(
    id_restaurante: int,
    id_produto: int,
    id_grupo: int,
    dados: GrupoComplementoUpdate,
    db: Session = Depends(get_db),
):
    return (
        grupo_complemento_controller
        .atualizar_grupo_complemento(
            db,
            id_restaurante,
            id_produto,
            id_grupo,
            dados,
        )
    )


# =========================================================
# ASSOCIAR / DESASSOCIAR
# =========================================================


@router.post(
    "/produtos/{id_produto}/grupos-complementos/{id_grupo}/associar",
    response_model=GrupoComplementoResponse,
)
def associar_grupo_produto(
    id_restaurante: int,
    id_produto: int,
    id_grupo: int,
    db: Session = Depends(get_db),
):
    return (
        grupo_complemento_controller
        .associar_grupo_produto(
            db,
            id_restaurante,
            id_produto,
            id_grupo,
        )
    )


@router.delete(
    "/produtos/{id_produto}/grupos-complementos/{id_grupo}/associar",
)
def desassociar_grupo_produto(
    id_restaurante: int,
    id_produto: int,
    id_grupo: int,
    db: Session = Depends(get_db),
):
    return (
        grupo_complemento_controller
        .desassociar_grupo_produto(
            db,
            id_restaurante,
            id_produto,
            id_grupo,
        )
    )


# =========================================================
# EXCLUSÃO
# =========================================================


@router.delete(
    "/grupos-complementos/{id_grupo}",
)
def deletar_grupo_complemento(
    id_restaurante: int,
    id_grupo: int,
    db: Session = Depends(get_db),
):
    return (
        grupo_complemento_controller
        .deletar_grupo_complemento(
            db,
            id_restaurante,
            id_grupo,
        )
    )
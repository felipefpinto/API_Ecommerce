from fastapi import HTTPException
from sqlalchemy.orm import Session

from api_ecommerce.models import ResponsavelRestaurante
from api_ecommerce.models.restaurante import Restaurante
from api_ecommerce.schemas import (
    ResponsavelRestauranteCreate,
    ResponsavelRestauranteUpdate,
    RestauranteStatus
)


def criar_responsavel(
    db: Session,
    responsavel: ResponsavelRestauranteCreate
):
    email_existente = (
        db.query(ResponsavelRestaurante)
        .filter(
            ResponsavelRestaurante.email == responsavel.email
        )
        .first()
    )

    if email_existente:
        raise HTTPException(
            status_code=400,
            detail="E-mail já cadastrado"
        )

    celular_existente = (
        db.query(ResponsavelRestaurante)
        .filter(
            ResponsavelRestaurante.celular == responsavel.celular
        )
        .first()
    )

    if celular_existente:
        raise HTTPException(
            status_code=400,
            detail="Celular já cadastrado"
        )

    novo_responsavel = ResponsavelRestaurante(
        nome=responsavel.nome,
        email=responsavel.email,
        celular=responsavel.celular,
    )

    db.add(novo_responsavel)
    db.commit()
    db.refresh(novo_responsavel)

    return novo_responsavel


def listar_responsaveis(db: Session):
    return db.query(ResponsavelRestaurante).all()


def buscar_responsavel(
    db: Session,
    id_responsavel: int
):
    responsavel = (
        db.query(ResponsavelRestaurante)
        .filter(
            ResponsavelRestaurante.id_responsavel == id_responsavel
        )
        .first()
    )

    if not responsavel:
        raise HTTPException(
            status_code=404,
            detail="Responsável não encontrado"
        )

    return responsavel


def buscar_responsavel_por_email(
    db: Session,
    email: str
):
    responsavel = (
        db.query(ResponsavelRestaurante)
        .filter(
            ResponsavelRestaurante.email == email
        )
        .first()
    )

    if not responsavel:
        raise HTTPException(
            status_code=404,
            detail="Responsável não encontrado"
        )

    return responsavel


def buscar_responsavel_por_celular(
    db: Session,
    celular: str
):
    responsavel = (
        db.query(ResponsavelRestaurante)
        .filter(
            ResponsavelRestaurante.celular == celular
        )
        .first()
    )

    if not responsavel:
        raise HTTPException(
            status_code=404,
            detail="Responsável não encontrado"
        )
    
    return responsavel


def atualizar_responsavel(
    db: Session,
    id_responsavel: int,
    responsavel_data: ResponsavelRestauranteUpdate
):
    responsavel = (
        db.query(ResponsavelRestaurante)
        .filter(
            ResponsavelRestaurante.id_responsavel == id_responsavel
        )
        .first()
    )

    if not responsavel:
        raise HTTPException(
            status_code=404,
            detail="Responsável não encontrado"
        )

    dados_atualizados = responsavel_data.model_dump(
        exclude_unset=True
    )

    for campo, valor in dados_atualizados.items():
        setattr(responsavel, campo, valor)

    db.commit()
    db.refresh(responsavel)

    return responsavel


def deletar_responsavel(
    db: Session,
    id_responsavel: int,
):
    responsavel = (
        db.query(
            ResponsavelRestaurante
        )
        .filter(
            ResponsavelRestaurante.id_responsavel
            == id_responsavel
        )
        .first()
    )

    if responsavel is None:
        raise HTTPException(
            status_code=404,
            detail="Responsável não encontrado",
        )

    # Verifica se existe algum restaurante
    # que NÃO esteja inativo.
    restaurante_nao_inativo = (
        db.query(Restaurante)
        .filter(
            Restaurante.responsavel_id
            == id_responsavel,
            Restaurante.status
            != RestauranteStatus.INATIVO.value,
        )
        .first()
    )

    if restaurante_nao_inativo:
        raise HTTPException(
            status_code=400,
            detail=(
                "Não é possível excluir a conta. "
                "Todos os restaurantes devem estar inativos."
            ),
        )

    try:
        db.delete(responsavel)

        db.commit()

        return {
            "message":
                "Conta e restaurantes excluídos com sucesso."
        }

    except Exception:
        db.rollback()

        raise
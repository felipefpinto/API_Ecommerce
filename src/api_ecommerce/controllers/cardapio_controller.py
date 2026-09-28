from fastapi import HTTPException
from sqlalchemy.orm import Session

from api_ecommerce.models.cardapio import Cardapio
from api_ecommerce.models.restaurante import Restaurante
from api_ecommerce.schemas.cardapio_schema import (
    CardapioCreate,
    CardapioUpdate,
)


def criar_cardapio(
    db: Session,
    id_restaurante: int,
    dados: CardapioCreate,
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

    cardapio = Cardapio(
        id_restaurante=id_restaurante,
        nome=dados.nome.strip(),
        descricao=(
            dados.descricao.strip()
            if dados.descricao
            else None
        ),
    )

    db.add(cardapio)
    db.commit()
    db.refresh(cardapio)

    return cardapio


def listar_cardapios(
    db: Session,
    id_restaurante: int,
):
    return (
        db.query(Cardapio)
        .filter(
            Cardapio.id_restaurante
            == id_restaurante
        )
        .order_by(
            Cardapio.id_cardapio
        )
        .all()
    )


def buscar_cardapio(
    db: Session,
    id_restaurante: int,
    id_cardapio: int,
):
    cardapio = (
        db.query(Cardapio)
        .filter(
            Cardapio.id_cardapio
            == id_cardapio,
            Cardapio.id_restaurante
            == id_restaurante,
        )
        .first()
    )

    if cardapio is None:
        raise HTTPException(
            status_code=404,
            detail="Cardápio não encontrado.",
        )

    return cardapio


def atualizar_cardapio(
    db: Session,
    id_restaurante: int,
    id_cardapio: int,
    dados: CardapioUpdate,
):
    cardapio = buscar_cardapio(
        db,
        id_restaurante,
        id_cardapio,
    )

    dados_update = (
        dados.model_dump(
            exclude_unset=True
        )
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
            dados_update[
                "descricao"
            ].strip()
        )

    for campo, valor in (
        dados_update.items()
    ):
        setattr(
            cardapio,
            campo,
            valor,
        )

    db.commit()
    db.refresh(cardapio)

    return cardapio


def deletar_cardapio(
    db: Session,
    id_restaurante: int,
    id_cardapio: int,
):
    cardapio = buscar_cardapio(
        db,
        id_restaurante,
        id_cardapio,
    )

    db.delete(cardapio)
    db.commit()

    return {
        "message":
            "Cardápio excluído com sucesso."
    }
from fastapi import HTTPException
from sqlalchemy.orm import Session

from api_ecommerce.models.cardapio import (
    Cardapio,
)
from api_ecommerce.models.secao_cardapio import (
    SecaoCardapio,
)
from api_ecommerce.schemas.secao_cardapio_schema import (
    SecaoCardapioCreate,
    SecaoCardapioUpdate,
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


def criar_secao(
    db: Session,
    id_restaurante: int,
    id_cardapio: int,
    dados: SecaoCardapioCreate,
):
    buscar_cardapio(
        db,
        id_restaurante,
        id_cardapio,
    )

    secao = SecaoCardapio(
        id_cardapio=id_cardapio,
        nome=dados.nome.strip(),
        descricao=(
            dados.descricao.strip()
            if dados.descricao
            else None
        ),
        ordem=dados.ordem,
    )

    db.add(secao)
    db.commit()
    db.refresh(secao)

    return secao


def listar_secoes(
    db: Session,
    id_restaurante: int,
    id_cardapio: int,
):
    buscar_cardapio(
        db,
        id_restaurante,
        id_cardapio,
    )

    return (
        db.query(SecaoCardapio)
        .filter(
            SecaoCardapio.id_cardapio
            == id_cardapio
        )
        .order_by(
            SecaoCardapio.ordem,
            SecaoCardapio.id_secao,
        )
        .all()
    )


def buscar_secao(
    db: Session,
    id_restaurante: int,
    id_cardapio: int,
    id_secao: int,
):
    buscar_cardapio(
        db,
        id_restaurante,
        id_cardapio,
    )

    secao = (
        db.query(SecaoCardapio)
        .filter(
            SecaoCardapio.id_secao
            == id_secao,
            SecaoCardapio.id_cardapio
            == id_cardapio,
        )
        .first()
    )

    if secao is None:
        raise HTTPException(
            status_code=404,
            detail="Seção não encontrada.",
        )

    return secao


def atualizar_secao(
    db: Session,
    id_restaurante: int,
    id_cardapio: int,
    id_secao: int,
    dados: SecaoCardapioUpdate,
):
    secao = buscar_secao(
        db,
        id_restaurante,
        id_cardapio,
        id_secao,
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
            secao,
            campo,
            valor,
        )

    db.commit()
    db.refresh(secao)

    return secao


def deletar_secao(
    db: Session,
    id_restaurante: int,
    id_cardapio: int,
    id_secao: int,
):
    secao = buscar_secao(
        db,
        id_restaurante,
        id_cardapio,
        id_secao,
    )

    db.delete(secao)
    db.commit()

    return {
        "message":
            "Seção excluída com sucesso."
    }
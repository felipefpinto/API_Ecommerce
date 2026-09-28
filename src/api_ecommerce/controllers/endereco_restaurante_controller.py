from fastapi import HTTPException
from sqlalchemy.orm import Session

from api_ecommerce.controllers import restaurante_controller
from api_ecommerce.controllers.endereco_controller import (
    geocodificar_endereco,
)

from api_ecommerce.models import (
    EnderecoRestaurante,
    Restaurante,
)
from api_ecommerce.schemas import (
    EnderecoRestauranteCreate,
    EnderecoRestauranteUpdate,
)


CAMPOS_OBRIGATORIOS = {
    "cep",
    "logradouro",
    "numero",
    "bairro",
    "cidade",
    "uf",
}


def buscar_restaurante(
    db: Session,
    id_restaurante: int,
) -> Restaurante:

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
            detail="Restaurante nao encontrado",
        )

    return restaurante


def buscar_endereco_restaurante(
    db: Session,
    id_restaurante: int,
) -> EnderecoRestaurante:

    endereco = (
        db.query(EnderecoRestaurante)
        .filter(
            EnderecoRestaurante.id_restaurante
            == id_restaurante
        )
        .first()
    )

    if endereco is None:
        raise HTTPException(
            status_code=404,
            detail="Endereco do restaurante nao encontrado",
        )

    return endereco


async def criar_endereco_restaurante(
    db: Session,
    id_restaurante: int,
    endereco_data: EnderecoRestauranteCreate,
) -> EnderecoRestaurante:

    buscar_restaurante(
        db,
        id_restaurante,
    )

    endereco_existente = (
        db.query(EnderecoRestaurante)
        .filter(
            EnderecoRestaurante.id_restaurante
            == id_restaurante
        )
        .first()
    )

    if endereco_existente:
        raise HTTPException(
            status_code=400,
            detail="Restaurante ja possui endereco cadastrado",
        )

    dados = endereco_data.model_dump()

    latitude = dados.get(
        "latitude"
    )

    longitude = dados.get(
        "longitude"
    )

    if (
        latitude is None
        or longitude is None
    ):
        latitude, longitude = (
            await geocodificar_endereco(
                logradouro=dados[
                    "logradouro"
                ],
                numero=dados[
                    "numero"
                ],
                cidade=dados[
                    "cidade"
                ],
                uf=dados[
                    "uf"
                ],
                cep=dados[
                    "cep"
                ],
            )
        )

        dados["latitude"] = latitude
        dados["longitude"] = longitude

    novo_endereco = EnderecoRestaurante(
        id_restaurante=id_restaurante,
        **dados,
    )

    try:
        db.add(
            novo_endereco
        )

        db.commit()

        db.refresh(
            novo_endereco
        )

        restaurante_controller.atualizar_status_restaurante(
            db,
            id_restaurante,
        )

        return novo_endereco

    except Exception:
        db.rollback()
        raise

async def atualizar_endereco_restaurante(
    db: Session,
    id_restaurante: int,
    endereco_data: EnderecoRestauranteUpdate,
) -> EnderecoRestaurante:

    endereco = buscar_endereco_restaurante(
        db,
        id_restaurante,
    )

    dados_atualizados = (
        endereco_data.model_dump(
            exclude_unset=True
        )
    )

    for campo in CAMPOS_OBRIGATORIOS:
        if (
            campo in dados_atualizados
            and dados_atualizados[campo]
            is None
        ):
            raise HTTPException(
                status_code=400,
                detail=f"{campo} nao pode ser nulo",
            )

    # Verifica se alguma informação
    # que interfere na localização mudou.
    campos_localizacao = {
        "cep",
        "logradouro",
        "numero",
        "bairro",
        "cidade",
        "uf",
    }

    endereco_alterado = any(
        campo in dados_atualizados
        for campo in campos_localizacao
    )

    for campo, valor in (
        dados_atualizados.items()
    ):
        setattr(
            endereco,
            campo,
            valor,
        )

    if endereco_alterado:
        latitude, longitude = (
            await geocodificar_endereco(
                logradouro=endereco.logradouro,
                numero=endereco.numero,
                cidade=endereco.cidade,
                uf=endereco.uf,
                cep=endereco.cep,
            )
        )

        endereco.latitude = latitude
        endereco.longitude = longitude

    try:
        db.commit()

        db.refresh(
            endereco
        )

        return endereco

    except Exception:
        db.rollback()
        raise


def deletar_endereco_restaurante(
    db: Session,
    id_restaurante: int,
) -> dict[str, str]:

    endereco = buscar_endereco_restaurante(
        db,
        id_restaurante,
    )

    try:
        db.delete(
            endereco
        )

        db.commit()

        restaurante_controller.atualizar_status_restaurante(
            db,
            id_restaurante,
        )

        return {
            "message":
                "Endereco do restaurante excluido com sucesso",
        }

    except Exception:
        db.rollback()
        raise
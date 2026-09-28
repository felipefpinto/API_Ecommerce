from fastapi import HTTPException
from sqlalchemy.orm import Session

import httpx
from decimal import Decimal

from api_ecommerce.models import Endereco, Usuario
from api_ecommerce.schemas import EnderecoCreate, EnderecoUpdate


CAMPOS_OBRIGATORIOS = {
    "cep",
    "logradouro",
    "numero",
    "bairro",
    "cidade",
    "uf",
}

async def geocodificar_endereco(
    logradouro: str,
    numero: str,
    bairro: str,
    cidade: str,
    uf: str,
    cep: str,
) -> tuple[Decimal, Decimal]:

    endereco_completo = (
        f"{logradouro}, {numero}, "
        f"{bairro}, {cidade}, {uf}, "
        f"{cep}, Brasil"
    )

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": endereco_completo,
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "br",
    }

    headers = {
        "User-Agent": "iComida/1.0 (projeto acadêmico)"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resposta = await client.get(
            url,
            params=params,
            headers=headers,
        )

    if resposta.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Erro ao consultar serviço de geocodificação",
        )

    resultados = resposta.json()

    if not resultados:
        raise HTTPException(
            status_code=422,
            detail="Não foi possível localizar o endereço informado",
        )

    resultado = resultados[0]

    return (
        Decimal(resultado["lat"]),
        Decimal(resultado["lon"]),
    )


def buscar_usuario(db: Session, id_usuario: int) -> Usuario:
    usuario = (
        db.query(Usuario)
        .filter(Usuario.id_usuario == id_usuario)
        .first()
    )

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario nao encontrado",
        )

    return usuario


def buscar_endereco_usuario(
    db: Session,
    id_usuario: int,
    id_endereco: int,
) -> Endereco:
    endereco = (
        db.query(Endereco)
        .filter(
            Endereco.id_endereco == id_endereco,
            Endereco.id_usuario == id_usuario,
        )
        .first()
    )

    if endereco is None:
        raise HTTPException(
            status_code=404,
            detail="Endereco nao encontrado",
        )

    return endereco


async def criar_endereco(
    db: Session,
    id_usuario: int,
    endereco_data: EnderecoCreate,
) -> Endereco:

    buscar_usuario(db, id_usuario)

    dados = endereco_data.model_dump()

    latitude = dados.get("latitude")
    longitude = dados.get("longitude")

    if latitude is None or longitude is None:

        latitude, longitude = await geocodificar_endereco(
            logradouro=dados["logradouro"],
            numero=dados["numero"],
            cidade=dados["cidade"],
            uf=dados["uf"],
            cep=dados["cep"],
        )

        dados["latitude"] = latitude
        dados["longitude"] = longitude

    novo_endereco = Endereco(
        id_usuario=id_usuario,
        **dados,
        ativo=False,
    )

    db.add(novo_endereco)
    db.commit()
    db.refresh(novo_endereco)

    return novo_endereco
async def geocodificar_endereco(
    logradouro: str,
    numero: str,
    cidade: str,
    uf: str,
    cep: str,
) -> tuple[Decimal, Decimal]:

    endereco_completo = (
        f"{logradouro}, {numero}, "
        f"{cidade}, {uf}, "
        f"{cep}, Brasil"
    )

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": endereco_completo,
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "br",
    }

    headers = {
        "User-Agent": "iComida/1.0"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resposta = await client.get(
            url,
            params=params,
            headers=headers,
        )

    if resposta.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Erro ao consultar serviço de geocodificação",
        )

    resultados = resposta.json()

    if not resultados:
        raise HTTPException(
            status_code=422,
            detail="Não foi possível localizar o endereço informado",
        )

    resultado = resultados[0]

    return (
        Decimal(resultado["lat"]),
        Decimal(resultado["lon"]),
    )

def listar_enderecos_usuario(
    db: Session,
    id_usuario: int,
) -> list[Endereco]:
    buscar_usuario(db, id_usuario)

    return (
        db.query(Endereco)
        .filter(
            Endereco.id_usuario == id_usuario,
        )
        .all()
    )


def atualizar_endereco(
    db: Session,
    id_usuario: int,
    id_endereco: int,
    endereco_data: EnderecoUpdate,
) -> Endereco:
    endereco = buscar_endereco_usuario(db, id_usuario, id_endereco)
    dados_atualizados = endereco_data.model_dump(exclude_unset=True)

    for campo in CAMPOS_OBRIGATORIOS:
        if campo in dados_atualizados and dados_atualizados[campo] is None:
            raise HTTPException(
                status_code=400,
                detail=f"{campo} nao pode ser nulo",
            )

    for campo, valor in dados_atualizados.items():
        setattr(endereco, campo, valor)

    db.commit()
    db.refresh(endereco)

    return endereco


def deletar_endereco(
    db: Session,
    id_usuario: int,
    id_endereco: int,
) -> dict[str, str]:
    endereco = buscar_endereco_usuario(db, id_usuario, id_endereco)

    db.delete(endereco)
    db.commit()

    return {
        "message": "Endereco excluido com sucesso",
    }

def definir_endereco_principal(
    db: Session,
    id_usuario: int,
    id_endereco: int,
) -> Endereco:

    
    endereco = buscar_endereco_usuario(
        db,
        id_usuario,
        id_endereco,
    )

    
    (
        db.query(Endereco)
        .filter(
            Endereco.id_usuario == id_usuario
        )
        .update(
            {
                Endereco.ativo: False
            },
            synchronize_session=False,
        )
    )

    endereco.ativo = True

    db.commit()

    db.refresh(endereco)

    return endereco
from fastapi import HTTPException
from sqlalchemy.orm import Session

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
            Endereco.ativo.is_(True),
        )
        .first()
    )

    if endereco is None:
        raise HTTPException(
            status_code=404,
            detail="Endereco nao encontrado",
        )

    return endereco


def criar_endereco(
    db: Session,
    id_usuario: int,
    endereco_data: EnderecoCreate,
) -> Endereco:
    buscar_usuario(db, id_usuario)

    novo_endereco = Endereco(
        id_usuario=id_usuario,
        **endereco_data.model_dump(),
    )

    db.add(novo_endereco)
    db.commit()
    db.refresh(novo_endereco)

    return novo_endereco


def listar_enderecos_usuario(
    db: Session,
    id_usuario: int,
) -> list[Endereco]:
    buscar_usuario(db, id_usuario)

    return (
        db.query(Endereco)
        .filter(
            Endereco.id_usuario == id_usuario,
            Endereco.ativo.is_(True),
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
    endereco.ativo = False

    db.commit()

    return {
        "message": "Endereco excluido com sucesso",
    }

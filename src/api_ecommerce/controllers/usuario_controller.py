from fastapi import HTTPException
from sqlalchemy.orm import Session

from api_ecommerce.models import Usuario
from api_ecommerce.schemas import *


def criar_usuario(db: Session, usuario: UsuarioCreate):

    usuario_existente = (
        db.query(Usuario)
        .filter(Usuario.email == usuario.email)
        .first()
    )

    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="E-mail já cadastrado"
        )

    if usuario.cpf is not None:
        cpf_existente = (
            db.query(Usuario)
            .filter(Usuario.cpf == usuario.cpf)
            .first()
    )

        if cpf_existente:
            raise HTTPException(
                status_code=400,
                detail="CPF já cadastrado"
            )


    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        celular=usuario.celular,
        cpf=usuario.cpf,
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


def listar_usuarios(db: Session):
    return db.query(Usuario).all()


def buscar_usuario(db: Session, id_usuario: int):

    usuario = (
        db.query(Usuario)
        .filter(Usuario.id_usuario == id_usuario)
        .first()
    )

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    return usuario


def atualizar_usuario(
    db: Session,
    id_usuario: int,
    usuario_data: UsuarioUpdate
):

    usuario = (
        db.query(Usuario)
        .filter(Usuario.id_usuario == id_usuario)
        .first()
    )

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    dados_atualizados = usuario_data.model_dump(exclude_unset=True)

    for campo, valor in dados_atualizados.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)

    return usuario


def deletar_usuario(db: Session, id_usuario: int):

    usuario = (
        db.query(Usuario)
        .filter(Usuario.id_usuario == id_usuario)
        .first()
    )

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    db.delete(usuario)
    db.commit()

    return {
        "message": "Usuário excluído com sucesso"
    }

def buscar_usuario_por_email(db, email: str):
    usuario = db.query(Usuario).filter(
        Usuario.email == email
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    return usuario

def buscar_usuario_por_celular(db, celular: str):
    usuario = db.query(Usuario).filter(
        Usuario.celular == celular
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    return usuario
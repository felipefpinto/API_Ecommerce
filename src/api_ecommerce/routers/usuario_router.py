from fastapi import APIRouter, Depends,Query, HTTPException
from sqlalchemy.orm import Session

from api_ecommerce.database import get_db
from api_ecommerce.schemas import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from api_ecommerce.controllers import usuario_controller
from api_ecommerce.models.usuario import Usuario

router = APIRouter(prefix="/usuario", tags=["Usuários"])


@router.post("/", response_model=UsuarioResponse)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    return usuario_controller.criar_usuario(db, usuario)


@router.get("/buscaremail", status_code=200)
def buscar_usuario_por_email(
    email: str = Query(...),
    db: Session = Depends(get_db)
):
    usuario_controller.buscar_usuario_por_email(db, email)
    return

@router.get("/buscarcelular", status_code=200)
def buscar_usuario_por_celular(
    celular: str = Query(...),
    db: Session = Depends(get_db)
):
    usuario_controller.buscar_usuario_por_celular(db, celular)
    return

@router.get("/dados-login")
def dados_login(
    email: str | None = Query(None),
    celular: str | None = Query(None),
    db: Session = Depends(get_db)
):
    if not email and not celular:
        raise HTTPException(
            status_code=400,
            detail="Informe o e-mail ou celular"
        )

    query = db.query(Usuario)

    if email:
        usuario = query.filter(
            Usuario.email == email
        ).first()

    else:
        usuario = query.filter(
            Usuario.celular == celular
        ).first()

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    return {
        "id_usuario": usuario.id_usuario,
        "nome": usuario.nome,
        "email": usuario.email
    }
    
@router.get("/telefone")
def buscar_telefone(
    email: str,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.email == email
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )
    numero_celular = str(usuario.celular)
    celular_mascarado = numero_celular[:2] + "*****" + numero_celular[-4:]
    
    return {
        "numero": celular_mascarado
    }

@router.get("/email")
def buscar_email(
    celular: str,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.celular == celular
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )
    
    email = usuario.email
    partes_email = email.split("@")
    nome_usuario = partes_email[0]
    dominio = partes_email[1]
    
    nome_usuario_mascarado = nome_usuario[0:2] + "****" + nome_usuario[-1:-3:-1][::-1]
    
    email_mascarado = nome_usuario_mascarado + "@" + dominio
    
    return {
        "email": email_mascarado
    }

@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return usuario_controller.listar_usuarios(db)


@router.get("/{id_usuario}", response_model=UsuarioResponse)
def buscar_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return usuario_controller.buscar_usuario(db, id_usuario)


@router.put("/{id_usuario}", response_model=UsuarioResponse)
def atualizar_usuario(id_usuario: int, usuario_data: UsuarioUpdate, db: Session = Depends(get_db)):
    return usuario_controller.atualizar_usuario(db, id_usuario, usuario_data)

@router.patch("/{id_usuario}",response_model=UsuarioResponse)
def atualizar_usuario(id_usuario: int,usuario: UsuarioUpdate,db: Session = Depends(get_db)):
    return usuario_controller.atualizar_usuario(
        db=db,
        id_usuario=id_usuario,
        usuario_data=usuario
    )

@router.delete("/{id_usuario}")
def deletar_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return usuario_controller.deletar_usuario(db, id_usuario)
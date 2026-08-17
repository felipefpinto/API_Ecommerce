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

    return {
        "celular": usuario.celular
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
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api_ecommerce.database import get_db
from api_ecommerce.schemas import UsuarioCreate, UsuarioResponse
from api_ecommerce.controllers import usuario_controller

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("/", response_model=UsuarioResponse)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    return usuario_controller.criar_usuario(db, usuario)


@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return usuario_controller.listar_usuarios(db)


@router.get("/{id_usuario}", response_model=UsuarioResponse)
def buscar_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return usuario_controller.buscar_usuario(db, id_usuario)


@router.put("/{id_usuario}", response_model=UsuarioResponse)
def atualizar_usuario(id_usuario: int, usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    return usuario_controller.atualizar_usuario(db, id_usuario, usuario_data)


@router.delete("/{id_usuario}")
def deletar_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return usuario_controller.deletar_usuario(db, id_usuario)
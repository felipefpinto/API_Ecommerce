from pydantic import BaseModel, EmailStr
from typing import Optional


class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    celular: str
    cpf: Optional[str] = None


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    celular: str | None = None
    cpf: str | None = None

class GoogleLoginRequest(BaseModel):
    credential: str


class UsuarioResponse(BaseModel):
    id_usuario: int
    nome: str
    email: EmailStr
    celular: str
    cpf: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
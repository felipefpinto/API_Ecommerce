from pydantic import BaseModel, EmailStr


class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    celular: str
    cpf: str


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    celular: str | None = None
    cpf: str | None = None


class UsuarioResponse(BaseModel):
    id_usuario: int
    nome: str
    email: EmailStr
    celular: str
    cpf: str

    model_config = {
        "from_attributes": True
    }
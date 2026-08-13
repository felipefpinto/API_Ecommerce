from pydantic import BaseModel, EmailStr


class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    celular: str
    cpf: str


class UsuarioResponse(BaseModel):
    id_usuario: int
    nome: str
    email: EmailStr
    celular: str
    cpf: str

    model_config = {
        "from_attributes": True
    }
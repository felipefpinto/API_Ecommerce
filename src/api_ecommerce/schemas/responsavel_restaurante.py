from pydantic import BaseModel, EmailStr


class ResponsavelRestauranteCreate(BaseModel):
    nome: str
    email: EmailStr
    celular: str


class ResponsavelRestauranteUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    celular: str | None = None


class ResponsavelRestauranteResponse(BaseModel):
    id_responsavel: int
    nome: str
    email: EmailStr
    celular: str
    ativo: bool

    model_config = {
        "from_attributes": True
    }
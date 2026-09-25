from pydantic import BaseModel, Field
from typing import Literal


class EnviarCodigoTelefoneRequest(BaseModel):
    celular: str = Field(..., min_length=10, max_length=15)


class VerificarCodigoTelefoneRequest(BaseModel):
    celular: str = Field(..., min_length=10, max_length=15)
    codigo: str = Field(..., min_length=6, max_length=6)


class VerificacaoResponse(BaseModel):
    sucesso: bool
    mensagem: str

class EnviarCodigoEmailRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)


class VerificarCodigoEmailRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    codigo: str = Field(..., min_length=6, max_length=6)

class EnviarCodigoTelefonePorEmailRequest(BaseModel):
    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
    )
    tipo: Literal["usuario", "responsavel"]


class EnviarCodigoEmailPorCelularRequest(BaseModel):
    celular: str = Field(
        ...,
        min_length=10,
        max_length=15,
    )
    tipo: Literal["usuario", "responsavel"]

class VerificarCodigoTelefonePorEmailRequest(BaseModel):
    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
    )
    codigo: str = Field(
        ...,
        min_length=6,
        max_length=6,
    )
    tipo: Literal["usuario", "responsavel"]

class VerificarCodigoEmailPorCelularRequest(BaseModel):
    celular: str = Field(
        ...,
        min_length=10,
        max_length=15,
    )
    codigo: str = Field(
        ...,
        min_length=6,
        max_length=6,
    )
    tipo: Literal["usuario", "responsavel"]
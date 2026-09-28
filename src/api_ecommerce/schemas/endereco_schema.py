from decimal import Decimal
import re

from pydantic import BaseModel, Field, field_validator


class EnderecoBase(BaseModel):
    apelido: str | None = Field(default=None, max_length=32)
    cep: str = Field(..., min_length=8, max_length=8)
    logradouro: str = Field(..., max_length=50)
    numero: str = Field(..., max_length=20)
    complemento: str | None = Field(default=None, max_length=50)
    bairro: str = Field(..., max_length=50)
    cidade: str = Field(..., max_length=50)
    uf: str = Field(..., min_length=2, max_length=2)
    ponto_referencia: str | None = Field(default=None, max_length=70)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)

    @field_validator("cep", mode="before")
    @classmethod
    def validar_cep(cls, cep: str) -> str:
        cep_normalizado = re.sub(r"\D", "", str(cep))

        if len(cep_normalizado) != 8:
            raise ValueError("CEP deve conter 8 digitos")

        return cep_normalizado

    @field_validator("uf", mode="before")
    @classmethod
    def validar_uf(cls, uf: str) -> str:
        uf_normalizada = str(uf).strip().upper()

        if len(uf_normalizada) != 2 or not uf_normalizada.isalpha():
            raise ValueError("UF deve conter 2 letras")

        return uf_normalizada


class EnderecoCreate(EnderecoBase):
    pass


class EnderecoUpdate(BaseModel):
    apelido: str | None = Field(default=None, max_length=32)
    cep: str | None = Field(default=None, min_length=8, max_length=8)
    logradouro: str | None = Field(default=None, max_length=50)
    numero: str | None = Field(default=None, max_length=20)
    complemento: str | None = Field(default=None, max_length=50)
    bairro: str | None = Field(default=None, max_length=50)
    cidade: str | None = Field(default=None, max_length=50)
    uf: str | None = Field(default=None, min_length=2, max_length=2)
    ponto_referencia: str | None = Field(default=None, max_length=70)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)

    @field_validator("cep", mode="before")
    @classmethod
    def validar_cep(cls, cep: str | None) -> str | None:
        if cep is None:
            return None

        cep_normalizado = re.sub(r"\D", "", str(cep))

        if len(cep_normalizado) != 8:
            raise ValueError("CEP deve conter 8 digitos")

        return cep_normalizado

    @field_validator("uf", mode="before")
    @classmethod
    def validar_uf(cls, uf: str | None) -> str | None:
        if uf is None:
            return None

        uf_normalizada = str(uf).strip().upper()

        if len(uf_normalizada) != 2 or not uf_normalizada.isalpha():
            raise ValueError("UF deve conter 2 letras")

        return uf_normalizada


class EnderecoResponse(EnderecoBase):
    id_endereco: int
    id_usuario: int
    ativo: bool

    model_config = {
        "from_attributes": True,
    }

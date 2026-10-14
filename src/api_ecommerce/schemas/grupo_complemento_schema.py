from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)


class GrupoComplementoCreate(BaseModel):
    nome: str = Field(
        ...,
        min_length=1,
        max_length=120,
    )

    descricao: str | None = Field(
        default=None,
        max_length=255,
    )

    obrigatorio: bool = False

    min_selecoes: int = Field(
        default=0,
        ge=0,
    )

    max_selecoes: int = Field(
        default=1,
        ge=1,
    )

    ordem: int = Field(
        default=0,
        ge=0,
    )

    @model_validator(mode="after")
    def validar_selecoes(self):
        if self.min_selecoes > self.max_selecoes:
            raise ValueError(
                "min_selecoes não pode ser maior "
                "que max_selecoes."
            )

        if self.obrigatorio and self.min_selecoes < 1:
            raise ValueError(
                "Grupos obrigatórios devem possuir "
                "min_selecoes maior ou igual a 1."
            )

        return self


class GrupoComplementoUpdate(BaseModel):
    nome: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
    )

    descricao: str | None = Field(
        default=None,
        max_length=255,
    )

    obrigatorio: bool | None = None

    min_selecoes: int | None = Field(
        default=None,
        ge=0,
    )

    max_selecoes: int | None = Field(
        default=None,
        ge=1,
    )

    ativo: bool | None = None

    ordem: int | None = Field(
        default=None,
        ge=0,
    )


class GrupoComplementoResponse(BaseModel):
    id_grupo: int
    id_restaurante: int

    nome: str
    descricao: str | None

    obrigatorio: bool

    min_selecoes: int
    max_selecoes: int

    ativo: bool
    ordem: int

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
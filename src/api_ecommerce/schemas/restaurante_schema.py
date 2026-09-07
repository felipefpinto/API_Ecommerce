from datetime import time
from enum import Enum
import re
import unicodedata

from pydantic import BaseModel, Field, field_validator, model_validator


class RestauranteStatus(str, Enum):
    PENDENTE = "PENDENTE"
    DISPONIVEL = "DISPONIVEL"
    INATIVO = "INATIVO"


class CanalVendaTipo(str, Enum):
    ENTREGA = "ENTREGA"
    RETIRADA = "RETIRADA"


class DiaSemana(str, Enum):
    SEGUNDA = "SEGUNDA"
    TERCA = "TERCA"
    QUARTA = "QUARTA"
    QUINTA = "QUINTA"
    SEXTA = "SEXTA"
    SABADO = "SABADO"
    DOMINGO = "DOMINGO"


def normalizar_texto(valor: object) -> str:
    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(char for char in texto if not unicodedata.combining(char))


def validar_cnpj_digitos(cnpj: str) -> bool:
    if len(cnpj) != 14 or len(set(cnpj)) == 1:
        return False

    pesos_primeiro = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_segundo = [6, *pesos_primeiro]

    soma = sum(int(digito) * peso for digito, peso in zip(cnpj[:12], pesos_primeiro))
    resto = soma % 11
    primeiro_digito = 0 if resto < 2 else 11 - resto

    soma = sum(int(digito) * peso for digito, peso in zip(cnpj[:13], pesos_segundo))
    resto = soma % 11
    segundo_digito = 0 if resto < 2 else 11 - resto

    return cnpj[-2:] == f"{primeiro_digito}{segundo_digito}"


class CanalVendaBase(BaseModel):
    tipo: CanalVendaTipo
    ativo: bool = True

    @field_validator("tipo", mode="before")
    @classmethod
    def validar_tipo(cls, tipo: object) -> str:
        tipo_normalizado = normalizar_texto(tipo)

        if tipo_normalizado not in CanalVendaTipo._value2member_map_:
            raise ValueError("Tipo deve ser ENTREGA ou RETIRADA")

        return tipo_normalizado

    model_config = {
        "use_enum_values": True,
    }


class CanalVendaCreate(CanalVendaBase):
    pass


class CanalVendaUpdate(BaseModel):
    tipo: CanalVendaTipo | None = None
    ativo: bool | None = None

    @field_validator("tipo", mode="before")
    @classmethod
    def validar_tipo(cls, tipo: object | None) -> str | None:
        if tipo is None:
            return None

        tipo_normalizado = normalizar_texto(tipo)

        if tipo_normalizado not in CanalVendaTipo._value2member_map_:
            raise ValueError("Tipo deve ser ENTREGA ou RETIRADA")

        return tipo_normalizado

    model_config = {
        "use_enum_values": True,
    }


class CanalVendaResponse(CanalVendaBase):
    id_canal_venda: int
    id_restaurante: int

    model_config = {
        "from_attributes": True,
        "use_enum_values": True,
    }


class HorarioFuncionamentoBase(BaseModel):
    dia_semana: DiaSemana
    hora_abertura: time
    hora_fechamento: time

    @field_validator("dia_semana", mode="before")
    @classmethod
    def validar_dia_semana(cls, dia_semana: object) -> str:
        dia_normalizado = normalizar_texto(dia_semana)

        if dia_normalizado not in DiaSemana._value2member_map_:
            raise ValueError("Dia da semana invalido")

        return dia_normalizado

    @model_validator(mode="after")
    def validar_intervalo_horario(self):
        if self.hora_abertura >= self.hora_fechamento:
            raise ValueError("Hora de abertura deve ser anterior a hora de fechamento")

        return self

    model_config = {
        "use_enum_values": True,
    }


class HorarioFuncionamentoCreate(HorarioFuncionamentoBase):
    pass


class HorarioFuncionamentoUpdate(BaseModel):
    dia_semana: DiaSemana | None = None
    hora_abertura: time | None = None
    hora_fechamento: time | None = None

    @field_validator("dia_semana", mode="before")
    @classmethod
    def validar_dia_semana(cls, dia_semana: object | None) -> str | None:
        if dia_semana is None:
            return None

        dia_normalizado = normalizar_texto(dia_semana)

        if dia_normalizado not in DiaSemana._value2member_map_:
            raise ValueError("Dia da semana invalido")

        return dia_normalizado

    model_config = {
        "use_enum_values": True,
    }


class HorarioFuncionamentoResponse(HorarioFuncionamentoBase):
    id_horario_funcionamento: int
    id_restaurante: int

    model_config = {
        "from_attributes": True,
        "use_enum_values": True,
    }


class RestauranteBase(BaseModel):
    razao_social: str = Field(..., max_length=150)
    nome_fantasia: str = Field(..., max_length=100)
    categoria: str = Field(..., max_length=50)
    descricao: str | None = Field(default=None, max_length=500)


class RestauranteCreate(RestauranteBase):
    cnpj: str = Field(..., min_length=14, max_length=14)
    responsavel_usuario_id: int
    canais_venda: list[CanalVendaCreate] = Field(default_factory=list)
    horarios_funcionamento: list[HorarioFuncionamentoCreate] = Field(
        default_factory=list,
    )

    @field_validator("cnpj", mode="before")
    @classmethod
    def validar_cnpj(cls, cnpj: object) -> str:
        cnpj_normalizado = re.sub(r"\D", "", str(cnpj))

        if not validar_cnpj_digitos(cnpj_normalizado):
            raise ValueError("CNPJ invalido")

        return cnpj_normalizado


class RestauranteUpdate(BaseModel):
    razao_social: str | None = Field(default=None, max_length=150)
    nome_fantasia: str | None = Field(default=None, max_length=100)
    categoria: str | None = Field(default=None, max_length=50)
    descricao: str | None = Field(default=None, max_length=500)
    status: RestauranteStatus | None = None

    @field_validator("status", mode="before")
    @classmethod
    def validar_status(cls, status: object | None) -> str | None:
        if status is None:
            return None

        status_normalizado = normalizar_texto(status)

        if status_normalizado not in RestauranteStatus._value2member_map_:
            raise ValueError("Status deve ser PENDENTE, DISPONIVEL ou INATIVO")

        return status_normalizado

    model_config = {
        "use_enum_values": True,
    }


class RestauranteResponse(RestauranteBase):
    id_restaurante: int
    cnpj: str
    status: RestauranteStatus
    responsavel_usuario_id: int
    canais_venda: list[CanalVendaResponse] = Field(default_factory=list)
    horarios_funcionamento: list[HorarioFuncionamentoResponse] = Field(
        default_factory=list,
    )

    model_config = {
        "from_attributes": True,
        "use_enum_values": True,
    }


class RestauranteCnpjResponse(BaseModel):
    id_restaurante: int
    cnpj: str
    nome_fantasia: str
    status: RestauranteStatus
    responsavel_email: str
    responsavel_celular: str

    model_config = {
        "use_enum_values": True,
    }

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FaixaEntregaCreate(BaseModel):
    distancia_min_km: Decimal = Field(
        ...,
        ge=0,
    )

    distancia_max_km: Decimal = Field(
        ...,
        gt=0,
    )

    taxa: Decimal = Field(
        ...,
        ge=0,
    )

    ordem: int = Field(
        default=0,
        ge=0,
    )

    ativo: bool = True

    @model_validator(mode="after")
    def validar_distancias(self):
        if self.distancia_max_km <= self.distancia_min_km:
            raise ValueError(
                "A distância máxima deve ser maior que a distância mínima."
            )

        return self


class FaixaEntregaUpdate(BaseModel):
    distancia_min_km: Decimal | None = Field(
        default=None,
        ge=0,
    )

    distancia_max_km: Decimal | None = Field(
        default=None,
        gt=0,
    )

    taxa: Decimal | None = Field(
        default=None,
        ge=0,
    )

    ordem: int | None = Field(
        default=None,
        ge=0,
    )

    ativo: bool | None = None


class FaixaEntregaResponse(BaseModel):
    id_faixa: int
    id_configuracao: int

    distancia_min_km: Decimal
    distancia_max_km: Decimal
    taxa: Decimal

    ativo: bool
    ordem: int

    model_config = ConfigDict(
        from_attributes=True
    )


class ConfiguracaoEntregaCreate(BaseModel):
    raio_entrega_km: Decimal = Field(
        ...,
        gt=0,
    )

    valor_minimo_pedido: Decimal = Field(
        default=0,
        ge=0,
    )

    entrega_gratis: bool = False

    valor_minimo_entrega_gratis: Decimal | None = Field(
        default=None,
        ge=0,
    )

    ativo: bool = True

    @model_validator(mode="after")
    def validar_entrega_gratis(self):
        if (
            self.entrega_gratis
            and self.valor_minimo_entrega_gratis is None
        ):
            raise ValueError(
                "Informe o valor mínimo para entrega grátis."
            )

        if not self.entrega_gratis:
            self.valor_minimo_entrega_gratis = None

        return self


class ConfiguracaoEntregaUpdate(BaseModel):
    raio_entrega_km: Decimal | None = Field(
        default=None,
        gt=0,
    )

    valor_minimo_pedido: Decimal | None = Field(
        default=None,
        ge=0,
    )

    entrega_gratis: bool | None = None

    valor_minimo_entrega_gratis: Decimal | None = Field(
        default=None,
        ge=0,
    )

    ativo: bool | None = None


class ConfiguracaoEntregaResponse(BaseModel):
    id_configuracao: int
    id_restaurante: int

    raio_entrega_km: Decimal
    valor_minimo_pedido: Decimal

    entrega_gratis: bool
    valor_minimo_entrega_gratis: Decimal | None

    ativo: bool

    faixas: list[FaixaEntregaResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )
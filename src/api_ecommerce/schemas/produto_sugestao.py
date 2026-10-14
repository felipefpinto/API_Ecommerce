from pydantic import BaseModel, ConfigDict, Field

from decimal import Decimal




class ProdutoSugestaoCreate(BaseModel):
    id_produto_sugerido: int = Field(
        ...,
        gt=0,
    )

    ordem: int = Field(
        default=0,
        ge=0,
    )


class ProdutoSugestaoUpdate(BaseModel):
    ordem: int | None = Field(
        default=None,
        ge=0,
    )

    ativo: bool | None = None
    

class ProdutoSugestaoResponse(BaseModel):
    id: int
    id_produto: int
    id_produto_sugerido: int
    ordem: int
    ativo: bool

    produto_sugerido: ProdutoSugeridoResponse

    model_config = ConfigDict(
        from_attributes=True,
    )


class ProdutoSugeridoResponse(BaseModel):
    id_produto: int
    nome: str
    descricao: str | None
    preco_base: Decimal
    imagem_url: str | None
    disponivel: bool
    ativo: bool

    model_config = ConfigDict(
        from_attributes=True,
    )
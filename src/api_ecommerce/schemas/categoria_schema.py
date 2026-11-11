from datetime import datetime

from pydantic import BaseModel


class CategoriaResponse(BaseModel):
    id: int
    nome: str
    descricao: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
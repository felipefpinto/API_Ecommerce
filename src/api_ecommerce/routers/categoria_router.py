from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api_ecommerce.controllers import categoria_controller
from api_ecommerce.database import get_db
from api_ecommerce.schemas import CategoriaResponse


router = APIRouter(
    prefix="/categorias",
    tags=["Categorias"],
)


@router.get(
    "/",
    response_model=list[CategoriaResponse],
)
def listar_categorias(
    db: Session = Depends(get_db),
):
    return categoria_controller.listar_categorias_ativas(db)
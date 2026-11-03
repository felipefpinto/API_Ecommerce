from sqlalchemy.orm import Session

from api_ecommerce.models import Categorias_restaurante


def listar_categorias_ativas(db: Session):
    return (
        db.query(Categorias_restaurante)
        .filter(Categorias_restaurante.status == "ATIVA")
        .order_by(Categorias_restaurante.nome.asc())
        .all()
    )
from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.orm import Session

from api_ecommerce.controllers import pedido_controller
from api_ecommerce.database.connection import get_db
from api_ecommerce.schemas.pedido import (
    PedidoCreate,
    PedidoResponse,
    PedidoStatusUpdate,
)

router = APIRouter(
    prefix="/usuarios/{id_usuario}/pedidos",
    tags=["Pedidos"],
)



@router.post(
    "",
    response_model=PedidoResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_pedido(
    id_usuario: int,
    dados: PedidoCreate,
    db: Session = Depends(get_db),
):
    return pedido_controller.criar_pedido(
        db=db,
        id_usuario=id_usuario,
        dados=dados,
    )

# =========================================================
# LISTAR PEDIDOS DO USUÁRIO
# =========================================================

@router.get(
    "",
    response_model=list[PedidoResponse],
)
def listar_pedidos(
    id_usuario: int,
    db: Session = Depends(get_db),
):
    return pedido_controller.listar_pedidos_usuario(
        db=db,
        id_usuario=id_usuario,
    )

# =========================================================
# BUSCAR PEDIDO DO USUÁRIO
# =========================================================

@router.get(
    "/{id_pedido}",
    response_model=PedidoResponse,
)
def buscar_pedido(
    id_usuario: int,
    id_pedido: int,
    db: Session = Depends(get_db),
):
    return pedido_controller.buscar_pedido_usuario(
        db=db,
        id_usuario=id_usuario,
        id_pedido=id_pedido,
    )

# =========================================================
# LISTAR PEDIDOS DO RESTAURANTE
# =========================================================

router_restaurante = APIRouter(
    prefix="/restaurantes/{id_restaurante}/pedidos",
    tags=["Pedidos - Restaurante"],
)

@router_restaurante.get(
    "",
    response_model=list[PedidoResponse],
)
def listar_pedidos_restaurante(
    id_restaurante: int,
    db: Session = Depends(get_db),
):
    return pedido_controller.listar_pedidos_restaurante(
        db=db,
        id_restaurante=id_restaurante,
    )

# =========================================================
# BUSCAR PEDIDO DO RESTAURANTE
# =========================================================

@router_restaurante.get(
    "/{id_pedido}",
    response_model=PedidoResponse,
)
def buscar_pedido_restaurante(
    id_restaurante: int,
    id_pedido: int,
    db: Session = Depends(get_db),
):
    return pedido_controller.buscar_pedido_restaurante(
        db=db,
        id_restaurante=id_restaurante,
        id_pedido=id_pedido,
    )

# =========================================================
# ATUALIZAR STATUS DO PEDIDO
# =========================================================

@router_restaurante.patch(
    "/{id_pedido}/status",
    response_model=PedidoResponse,
)
def atualizar_status_pedido(
    id_restaurante: int,
    id_pedido: int,
    dados: PedidoStatusUpdate,
    db: Session = Depends(get_db),
):
    return pedido_controller.atualizar_status_pedido(
        db=db,
        id_restaurante=id_restaurante,
        id_pedido=id_pedido,
        novo_status=dados.status,
    )

# =========================================================
# ACEITAR PEDIDO
# =========================================================

@router_restaurante.patch(
    "/{id_pedido}/aceitar",
    response_model=PedidoResponse,
)
def aceitar_pedido(
    id_restaurante: int,
    id_pedido: int,
    db: Session = Depends(get_db),
):
    return pedido_controller.aceitar_pedido(
        db=db,
        id_restaurante=id_restaurante,
        id_pedido=id_pedido,
    )


# =========================================================
# RECUSAR PEDIDO
# =========================================================

@router_restaurante.patch(
    "/{id_pedido}/recusar",
    response_model=PedidoResponse,
)
def recusar_pedido(
    id_restaurante: int,
    id_pedido: int,
    db: Session = Depends(get_db),
):
    return pedido_controller.recusar_pedido(
        db=db,
        id_restaurante=id_restaurante,
        id_pedido=id_pedido,
    )
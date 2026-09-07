from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from api_ecommerce.controllers import restaurante_controller
from api_ecommerce.database import get_db
from api_ecommerce.schemas import (
    CanalVendaCreate,
    CanalVendaResponse,
    CanalVendaUpdate,
    HorarioFuncionamentoCreate,
    HorarioFuncionamentoResponse,
    HorarioFuncionamentoUpdate,
    RestauranteCnpjResponse,
    RestauranteCreate,
    RestauranteResponse,
    RestauranteUpdate,
)


router = APIRouter(
    prefix="/restaurantes",
    tags=["Restaurantes"],
)


@router.post(
    "/",
    response_model=RestauranteResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_restaurante(
    restaurante_data: RestauranteCreate,
    db: Session = Depends(get_db),
):
    return restaurante_controller.criar_restaurante(db, restaurante_data)


@router.get("/", response_model=list[RestauranteResponse])
def listar_restaurantes(db: Session = Depends(get_db)):
    return restaurante_controller.listar_restaurantes(db)


@router.get("/disponiveis", response_model=list[RestauranteResponse])
def listar_restaurantes_disponiveis(db: Session = Depends(get_db)):
    return restaurante_controller.listar_restaurantes_disponiveis(db)


@router.get("/buscar-cnpj", response_model=RestauranteCnpjResponse)
def buscar_restaurante_por_cnpj(
    cnpj: str = Query(...),
    db: Session = Depends(get_db),
):
    return restaurante_controller.buscar_dados_cnpj(db, cnpj)


@router.get("/{id_restaurante}", response_model=RestauranteResponse)
def buscar_restaurante(
    id_restaurante: int,
    db: Session = Depends(get_db),
):
    return restaurante_controller.buscar_restaurante(db, id_restaurante)


@router.patch("/{id_restaurante}", response_model=RestauranteResponse)
def atualizar_restaurante(
    id_restaurante: int,
    restaurante_data: RestauranteUpdate,
    db: Session = Depends(get_db),
):
    return restaurante_controller.atualizar_restaurante(
        db,
        id_restaurante,
        restaurante_data,
    )


@router.delete("/{id_restaurante}")
def deletar_restaurante(
    id_restaurante: int,
    db: Session = Depends(get_db),
):
    return restaurante_controller.deletar_restaurante(db, id_restaurante)


@router.post(
    "/{id_restaurante}/canais-venda",
    response_model=CanalVendaResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_canal_venda(
    id_restaurante: int,
    canal_venda_data: CanalVendaCreate,
    db: Session = Depends(get_db),
):
    return restaurante_controller.criar_canal_venda(
        db,
        id_restaurante,
        canal_venda_data,
    )


@router.get(
    "/{id_restaurante}/canais-venda",
    response_model=list[CanalVendaResponse],
)
def listar_canais_venda(
    id_restaurante: int,
    db: Session = Depends(get_db),
):
    return restaurante_controller.listar_canais_venda(db, id_restaurante)


@router.patch(
    "/{id_restaurante}/canais-venda/{id_canal_venda}",
    response_model=CanalVendaResponse,
)
def atualizar_canal_venda(
    id_restaurante: int,
    id_canal_venda: int,
    canal_venda_data: CanalVendaUpdate,
    db: Session = Depends(get_db),
):
    return restaurante_controller.atualizar_canal_venda(
        db,
        id_restaurante,
        id_canal_venda,
        canal_venda_data,
    )


@router.delete("/{id_restaurante}/canais-venda/{id_canal_venda}")
def deletar_canal_venda(
    id_restaurante: int,
    id_canal_venda: int,
    db: Session = Depends(get_db),
):
    return restaurante_controller.deletar_canal_venda(
        db,
        id_restaurante,
        id_canal_venda,
    )


@router.post(
    "/{id_restaurante}/horarios-funcionamento",
    response_model=HorarioFuncionamentoResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_horario_funcionamento(
    id_restaurante: int,
    horario_data: HorarioFuncionamentoCreate,
    db: Session = Depends(get_db),
):
    return restaurante_controller.criar_horario_funcionamento(
        db,
        id_restaurante,
        horario_data,
    )


@router.get(
    "/{id_restaurante}/horarios-funcionamento",
    response_model=list[HorarioFuncionamentoResponse],
)
def listar_horarios_funcionamento(
    id_restaurante: int,
    db: Session = Depends(get_db),
):
    return restaurante_controller.listar_horarios_funcionamento(
        db,
        id_restaurante,
    )


@router.patch(
    "/{id_restaurante}/horarios-funcionamento/{id_horario_funcionamento}",
    response_model=HorarioFuncionamentoResponse,
)
def atualizar_horario_funcionamento(
    id_restaurante: int,
    id_horario_funcionamento: int,
    horario_data: HorarioFuncionamentoUpdate,
    db: Session = Depends(get_db),
):
    return restaurante_controller.atualizar_horario_funcionamento(
        db,
        id_restaurante,
        id_horario_funcionamento,
        horario_data,
    )


@router.delete(
    "/{id_restaurante}/horarios-funcionamento/{id_horario_funcionamento}"
)
def deletar_horario_funcionamento(
    id_restaurante: int,
    id_horario_funcionamento: int,
    db: Session = Depends(get_db),
):
    return restaurante_controller.deletar_horario_funcionamento(
        db,
        id_restaurante,
        id_horario_funcionamento,
    )

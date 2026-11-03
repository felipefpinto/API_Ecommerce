from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api_ecommerce.controllers import configuracao_entrega_controller
from api_ecommerce.database.connection import get_db
from api_ecommerce.schemas.configuracao_entrega import (
    ConfiguracaoEntregaCreate,
    ConfiguracaoEntregaResponse,
    ConfiguracaoEntregaUpdate,
    FaixaEntregaCreate,
    FaixaEntregaResponse,
    FaixaEntregaUpdate,
)
from api_ecommerce.services.entrega_service import (
    calcular_entrega,
)

router = APIRouter(
    prefix="/restaurantes/{id_restaurante}/configuracao-entrega",
    tags=["Configuração de entrega"],
)


@router.post(
    "/",
    response_model=ConfiguracaoEntregaResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_configuracao(
    id_restaurante: int,
    dados: ConfiguracaoEntregaCreate,
    db: Session = Depends(get_db),
):
    return configuracao_entrega_controller.criar_configuracao(
        db=db,
        id_restaurante=id_restaurante,
        dados=dados,
    )


@router.get(
    "/",
    response_model=ConfiguracaoEntregaResponse,
)
def buscar_configuracao(
    id_restaurante: int,
    db: Session = Depends(get_db),
):
    return configuracao_entrega_controller.buscar_configuracao(
        db=db,
        id_restaurante=id_restaurante,
    )


@router.patch(
    "/",
    response_model=ConfiguracaoEntregaResponse,
)
def atualizar_configuracao(
    id_restaurante: int,
    dados: ConfiguracaoEntregaUpdate,
    db: Session = Depends(get_db),
):
    return configuracao_entrega_controller.atualizar_configuracao(
        db=db,
        id_restaurante=id_restaurante,
        dados=dados,
    )

@router.post(
    "/faixas/",
    response_model=FaixaEntregaResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_faixa(
    id_restaurante: int,
    dados: FaixaEntregaCreate,
    db: Session = Depends(get_db),
):
    return configuracao_entrega_controller.criar_faixa(
        db=db,
        id_restaurante=id_restaurante,
        dados=dados,
    )

@router.patch(
    "/faixas/{id_faixa}",
    response_model=FaixaEntregaResponse,
)
def atualizar_faixa(
    id_restaurante: int,
    id_faixa: int,
    dados: FaixaEntregaUpdate,
    db: Session = Depends(get_db),
):
    return configuracao_entrega_controller.atualizar_faixa(
        db=db,
        id_restaurante=id_restaurante,
        id_faixa=id_faixa,
        dados=dados,
    )


@router.delete(
    "/faixas/{id_faixa}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deletar_faixa(
    id_restaurante: int,
    id_faixa: int,
    db: Session = Depends(get_db),
):
    configuracao_entrega_controller.deletar_faixa(
        db=db,
        id_restaurante=id_restaurante,
        id_faixa=id_faixa,
    )

@router.get(
    "/calcular/{id_endereco}",
)
def consultar_entrega(
    id_restaurante: int,
    id_endereco: int,
    db: Session = Depends(get_db),
):
    return calcular_entrega(
        db=db,
        id_restaurante=id_restaurante,
        id_endereco=id_endereco,
    )
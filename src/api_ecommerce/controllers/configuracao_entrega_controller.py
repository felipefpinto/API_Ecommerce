from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api_ecommerce.models.configuracao_entrega import (
    ConfiguracaoEntrega,
    FaixaEntrega,
)
from api_ecommerce.models.restaurante import Restaurante
from api_ecommerce.schemas.configuracao_entrega import (
    ConfiguracaoEntregaCreate,
    ConfiguracaoEntregaUpdate,
    FaixaEntregaCreate,
    FaixaEntregaUpdate,
)

def criar_configuracao(
    db: Session,
    id_restaurante: int,
    dados: ConfiguracaoEntregaCreate,
):
    # Verifica se o restaurante existe
    restaurante = (
        db.query(Restaurante)
        .filter(
            Restaurante.id_restaurante == id_restaurante
        )
        .first()
    )

    if not restaurante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurante não encontrado.",
        )

    # Cada restaurante pode ter apenas uma configuração
    configuracao_existente = (
        db.query(ConfiguracaoEntrega)
        .filter(
            ConfiguracaoEntrega.id_restaurante
            == id_restaurante
        )
        .first()
    )

    if configuracao_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Este restaurante já possui "
                "uma configuração de entrega."
            ),
        )

    configuracao = ConfiguracaoEntrega(
        id_restaurante=id_restaurante,
        raio_entrega_km=dados.raio_entrega_km,
        valor_minimo_pedido=dados.valor_minimo_pedido,
        entrega_gratis=dados.entrega_gratis,
        valor_minimo_entrega_gratis=(
            dados.valor_minimo_entrega_gratis
        ),
        ativo=dados.ativo,
    )

    db.add(configuracao)
    db.commit()
    db.refresh(configuracao)

    return configuracao


def buscar_configuracao(
    db: Session,
    id_restaurante: int,
):
    configuracao = (
        db.query(ConfiguracaoEntrega)
        .filter(
            ConfiguracaoEntrega.id_restaurante
            == id_restaurante
        )
        .first()
    )

    if not configuracao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Configuração de entrega "
                "não encontrada."
            ),
        )

    return configuracao


def atualizar_configuracao(
    db: Session,
    id_restaurante: int,
    dados: ConfiguracaoEntregaUpdate,
):
    configuracao = buscar_configuracao(
        db,
        id_restaurante,
    )

    dados_update = dados.model_dump(
        exclude_unset=True
    )

    for campo, valor in dados_update.items():
        setattr(
            configuracao,
            campo,
            valor,
        )

    # Regra da entrega grátis
    if configuracao.entrega_gratis:
        if (
            configuracao.valor_minimo_entrega_gratis
            is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Informe o valor mínimo "
                    "para entrega grátis."
                ),
            )
    else:
        configuracao.valor_minimo_entrega_gratis = None

    db.commit()
    db.refresh(configuracao)

    return configuracao


def criar_faixa(
    db: Session,
    id_restaurante: int,
    dados: FaixaEntregaCreate,
):
    configuracao = buscar_configuracao(
        db,
        id_restaurante,
    )

    # Não permite ultrapassar o raio máximo
    if (
        dados.distancia_max_km
        > configuracao.raio_entrega_km
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "A distância máxima da faixa "
                "não pode ultrapassar o raio "
                "de entrega do restaurante."
            ),
        )

    # Verifica se a nova faixa cruza
    # alguma faixa já cadastrada
    faixas_existentes = (
        db.query(FaixaEntrega)
        .filter(
            FaixaEntrega.id_configuracao
            == configuracao.id_configuracao
        )
        .all()
    )

    for faixa in faixas_existentes:
        sobrepoe = (
            dados.distancia_min_km
            < faixa.distancia_max_km
            and
            dados.distancia_max_km
            > faixa.distancia_min_km
        )

        if sobrepoe:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Esta faixa de distância "
                    "sobrepõe uma faixa já cadastrada."
                ),
            )

    faixa = FaixaEntrega(
        id_configuracao=configuracao.id_configuracao,
        distancia_min_km=dados.distancia_min_km,
        distancia_max_km=dados.distancia_max_km,
        taxa=dados.taxa,
        ativo=dados.ativo,
        ordem=dados.ordem,
    )

    db.add(faixa)
    db.commit()
    db.refresh(faixa)

    return faixa    

def atualizar_faixa(
    db: Session,
    id_restaurante: int,
    id_faixa: int,
    dados: FaixaEntregaUpdate,
):
    configuracao = buscar_configuracao(
        db,
        id_restaurante,
    )

    faixa = (
        db.query(FaixaEntrega)
        .filter(
            FaixaEntrega.id_faixa == id_faixa,
            FaixaEntrega.id_configuracao
            == configuracao.id_configuracao,
        )
        .first()
    )

    if not faixa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faixa de entrega não encontrada.",
        )

    dados_update = dados.model_dump(
        exclude_unset=True
    )

    nova_distancia_min = dados_update.get(
        "distancia_min_km",
        faixa.distancia_min_km,
    )

    nova_distancia_max = dados_update.get(
        "distancia_max_km",
        faixa.distancia_max_km,
    )

    # Distância máxima precisa ser maior que a mínima
    if nova_distancia_max <= nova_distancia_min:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "A distância máxima deve ser maior "
                "que a distância mínima."
            ),
        )

    # Não pode ultrapassar o raio máximo
    if (
        nova_distancia_max
        > configuracao.raio_entrega_km
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "A distância máxima da faixa "
                "não pode ultrapassar o raio "
                "de entrega do restaurante."
            ),
        )

    # Verifica sobreposição com as OUTRAS faixas
    outras_faixas = (
        db.query(FaixaEntrega)
        .filter(
            FaixaEntrega.id_configuracao
            == configuracao.id_configuracao,
            FaixaEntrega.id_faixa != id_faixa,
        )
        .all()
    )

    for outra_faixa in outras_faixas:
        sobrepoe = (
            nova_distancia_min
            < outra_faixa.distancia_max_km
            and
            nova_distancia_max
            > outra_faixa.distancia_min_km
        )

        if sobrepoe:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Esta faixa de distância "
                    "sobrepõe uma faixa já cadastrada."
                ),
            )

    for campo, valor in dados_update.items():
        setattr(
            faixa,
            campo,
            valor,
        )

    db.commit()
    db.refresh(faixa)

    return faixa


def deletar_faixa(
    db: Session,
    id_restaurante: int,
    id_faixa: int,
):
    configuracao = buscar_configuracao(
        db,
        id_restaurante,
    )

    faixa = (
        db.query(FaixaEntrega)
        .filter(
            FaixaEntrega.id_faixa == id_faixa,
            FaixaEntrega.id_configuracao
            == configuracao.id_configuracao,
        )
        .first()
    )

    if not faixa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faixa de entrega não encontrada.",
        )

    db.delete(faixa)
    db.commit()
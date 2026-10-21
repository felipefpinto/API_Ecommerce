from math import atan2, cos, radians, sin, sqrt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api_ecommerce.models.endereco import Endereco
from api_ecommerce.models.endereco_restaurante import EnderecoRestaurante
from api_ecommerce.models.configuracao_entrega import (
    ConfiguracaoEntrega,
    FaixaEntrega,
)

def calcular_distancia_km(
    latitude_origem,
    longitude_origem,
    latitude_destino,
    longitude_destino,
) -> float:
    """
    Calcula a distância em linha reta entre
    duas coordenadas utilizando a fórmula
    de Haversine.

    Retorna a distância em quilômetros.
    """

    raio_terra_km = 6371.0

    lat1 = radians(float(latitude_origem))
    lon1 = radians(float(longitude_origem))

    lat2 = radians(float(latitude_destino))
    lon2 = radians(float(longitude_destino))

    diferenca_lat = lat2 - lat1
    diferenca_lon = lon2 - lon1

    a = (
        sin(diferenca_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(diferenca_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a),
    )

    distancia = raio_terra_km * c

    return round(distancia, 2)

def calcular_entrega(
    db: Session,
    id_restaurante: int,
    id_endereco: int,
):
    # Busca o endereço do usuário
    endereco_usuario = (
        db.query(Endereco)
        .filter(
            Endereco.id_endereco == id_endereco
        )
        .first()
    )

    if not endereco_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereço do usuário não encontrado.",
        )

    # Verifica se o endereço possui coordenadas
    if (
        endereco_usuario.latitude is None
        or endereco_usuario.longitude is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "O endereço do usuário não possui "
                "latitude e longitude."
            ),
        )

    # Busca o endereço do restaurante
    endereco_restaurante = (
        db.query(EnderecoRestaurante)
        .filter(
            EnderecoRestaurante.id_restaurante
            == id_restaurante
        )
        .first()
    )

    if not endereco_restaurante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereço do restaurante não encontrado.",
        )

    # Verifica se o restaurante possui coordenadas
    if (
        endereco_restaurante.latitude is None
        or endereco_restaurante.longitude is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "O endereço do restaurante não possui "
                "latitude e longitude."
            ),
        )

    # Busca a configuração de entrega
    configuracao = (
        db.query(ConfiguracaoEntrega)
        .filter(
            ConfiguracaoEntrega.id_restaurante
            == id_restaurante,
            ConfiguracaoEntrega.ativo.is_(True),
        )
        .first()
    )

    if not configuracao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Este restaurante não possui uma "
                "configuração de entrega ativa."
            ),
        )

    # Calcula a distância
    distancia_km = calcular_distancia_km(
        endereco_usuario.latitude,
        endereco_usuario.longitude,
        endereco_restaurante.latitude,
        endereco_restaurante.longitude,
    )

    # Verifica se está fora do raio
    if distancia_km > float(
        configuracao.raio_entrega_km
    ):
        return {
            "distancia_km": distancia_km,
            "dentro_area_entrega": False,
            "taxa_entrega": None,
            "valor_minimo_pedido": float(
                configuracao.valor_minimo_pedido
            ),
        }

    # Procura a faixa correspondente
    faixas = (
        db.query(FaixaEntrega)
        .filter(
            FaixaEntrega.id_configuracao
            == configuracao.id_configuracao,
            FaixaEntrega.ativo.is_(True),
        )
        .order_by(
            FaixaEntrega.distancia_min_km
        )
        .all()
    )

    faixa_encontrada = None

    for faixa in faixas:
        distancia_min = float(
            faixa.distancia_min_km
        )

        distancia_max = float(
            faixa.distancia_max_km
        )

        if (
            distancia_km >= distancia_min
            and distancia_km <= distancia_max
        ):
            faixa_encontrada = faixa
            break

    if not faixa_encontrada:
        return {
            "distancia_km": distancia_km,
            "dentro_area_entrega": True,
            "taxa_entrega": None,
            "valor_minimo_pedido": float(
                configuracao.valor_minimo_pedido
            ),
        }

    return {
        "distancia_km": distancia_km,
        "dentro_area_entrega": True,
        "taxa_entrega": float(
            faixa_encontrada.taxa
        ),
        "valor_minimo_pedido": float(
            configuracao.valor_minimo_pedido
        ),
    }
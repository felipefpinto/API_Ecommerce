from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api_ecommerce.core.config import settings

from api_ecommerce.database import get_db

from api_ecommerce.schemas.verificacao_schema import (
    EnviarCodigoTelefoneRequest,
    VerificarCodigoTelefoneRequest,
    EnviarCodigoEmailRequest,
    VerificarCodigoEmailRequest,
    VerificacaoResponse,
    EnviarCodigoTelefonePorEmailRequest,
    EnviarCodigoEmailPorCelularRequest,
    VerificarCodigoTelefonePorEmailRequest,
    VerificarCodigoEmailPorCelularRequest,
)
from api_ecommerce.services.verificacao_service import (
    enviar_codigo_telefone,
    verificar_codigo_telefone,
    enviar_codigo_email,
    verificar_codigo_email,

)

from api_ecommerce.models.usuario import Usuario
from api_ecommerce.models.responsavel_restaurante import ResponsavelRestaurante


router = APIRouter(
    prefix="/verificacao",
    tags=["Verificação"],
)


@router.post(
    "/telefone/enviar",
    response_model=VerificacaoResponse,
)
def enviar_codigo(dados: EnviarCodigoTelefoneRequest):
    return enviar_codigo_telefone(dados.celular)

@router.post(
    "/telefone/enviar-por-email",
    response_model=VerificacaoResponse,
)
def enviar_codigo_telefone_por_email(
    dados: EnviarCodigoTelefonePorEmailRequest,
    db: Session = Depends(get_db),
):
    email = dados.email.strip().lower()

    if dados.tipo == "usuario":
        pessoa = (
            db.query(Usuario)
            .filter(Usuario.email == email)
            .first()
        )
    else:
        pessoa = (
            db.query(ResponsavelRestaurante)
            .filter(ResponsavelRestaurante.email == email)
            .first()
        )

    if pessoa is None:
        raise HTTPException(
            status_code=404,
            detail="Cadastro não encontrado.",
        )

    if not pessoa.celular:
        raise HTTPException(
            status_code=404,
            detail="Celular não encontrado.",
        )

    return enviar_codigo_telefone(
        str(pessoa.celular)
    )

@router.post(
    "/telefone/verificar",
    response_model=VerificacaoResponse,
)
def verificar_codigo(dados: VerificarCodigoTelefoneRequest):
    return verificar_codigo_telefone(
        dados.celular,
        dados.codigo,
    )

@router.post(
    "/email/enviar",
    response_model=VerificacaoResponse,
)
def enviar_codigo_email_endpoint(
    dados: EnviarCodigoEmailRequest,
):
    return enviar_codigo_email(dados.email)

@router.post(
    "/email/enviar-por-celular",
    response_model=VerificacaoResponse,
)
def enviar_codigo_email_por_celular(
    dados: EnviarCodigoEmailPorCelularRequest,
    db: Session = Depends(get_db),
):
    celular = dados.celular.strip()

    if dados.tipo == "usuario":
        pessoa = (
            db.query(Usuario)
            .filter(Usuario.celular == celular)
            .first()
        )
    else:
        pessoa = (
            db.query(ResponsavelRestaurante)
            .filter(ResponsavelRestaurante.celular == celular)
            .first()
        )

    if pessoa is None:
        raise HTTPException(
            status_code=404,
            detail="Cadastro não encontrado.",
        )

    if not pessoa.email:
        raise HTTPException(
            status_code=404,
            detail="E-mail não encontrado.",
        )

    return enviar_codigo_email(
        pessoa.email
    )

@router.post(
    "/email/verificar",
    response_model=VerificacaoResponse,
)
def verificar_codigo_email_endpoint(
    dados: VerificarCodigoEmailRequest,
):
    return verificar_codigo_email(
        dados.email,
        dados.codigo,
    )


@router.post(
    "/telefone/verificar-por-email",
    response_model=VerificacaoResponse,
)
def verificar_codigo_telefone_por_email(
    dados: VerificarCodigoTelefonePorEmailRequest,
    db: Session = Depends(get_db),
):
    email = dados.email.strip().lower()

    if dados.tipo == "usuario":
        pessoa = (
            db.query(Usuario)
            .filter(Usuario.email == email)
            .first()
        )
    else:
        pessoa = (
            db.query(ResponsavelRestaurante)
            .filter(ResponsavelRestaurante.email == email)
            .first()
        )

    if pessoa is None:
        raise HTTPException(
            status_code=404,
            detail="Cadastro não encontrado.",
        )

    if not pessoa.celular:
        raise HTTPException(
            status_code=404,
            detail="Celular não encontrado.",
        )

    return verificar_codigo_telefone(
        str(pessoa.celular),
        dados.codigo,
    )

@router.post(
    "/email/verificar-por-celular",
    response_model=VerificacaoResponse,
)
def verificar_codigo_email_por_celular(
    dados: VerificarCodigoEmailPorCelularRequest,
    db: Session = Depends(get_db),
):
    celular = dados.celular.strip()

    if dados.tipo == "usuario":
        pessoa = (
            db.query(Usuario)
            .filter(Usuario.celular == celular)
            .first()
        )
    else:
        pessoa = (
            db.query(ResponsavelRestaurante)
            .filter(
                ResponsavelRestaurante.celular == celular
            )
            .first()
        )

    if pessoa is None:
        raise HTTPException(
            status_code=404,
            detail="Cadastro não encontrado.",
        )

    if not pessoa.email:
        raise HTTPException(
            status_code=404,
            detail="E-mail não encontrado.",
        )

    return verificar_codigo_email(
        pessoa.email,
        dados.codigo,
    )
import re

from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo

"""from api_ecommerce.models import (
    CanalVenda,
    HorarioFuncionamento,
    Restaurante,
    ResponsavelRestaurante,
)"""
from api_ecommerce.models import (
    CanalVenda,
    Categorias_restaurante,
    HorarioFuncionamento,
    Restaurante,
    RestauranteCategoria,
    ResponsavelRestaurante,
    EnderecoRestaurante
)
from api_ecommerce.schemas import (
    CanalVendaCreate,
    CanalVendaUpdate,
    HorarioFuncionamentoCreate,
    HorarioFuncionamentoUpdate,
    RestauranteCreate,
    RestauranteStatus,
    RestauranteUpdate,
)
from api_ecommerce.schemas.restaurante_schema import validar_cnpj_digitos


CAMPOS_RESTAURANTE_OBRIGATORIOS = {
    "razao_social",
    "nome_fantasia",
    "status",
}
CAMPOS_CANAL_VENDA_OBRIGATORIOS = {
    "tipo",
    "ativo",
}
CAMPOS_HORARIO_FUNCIONAMENTO_OBRIGATORIOS = {
    "dia_semana",
    "hora_abertura",
    "hora_fechamento",
}


def buscar_responsavel(
    db: Session,
    id_responsavel: int,
) -> ResponsavelRestaurante:
    responsavel = (
        db.query(ResponsavelRestaurante)
        .filter(
            ResponsavelRestaurante.id_responsavel
            == id_responsavel
        )
        .first()
    )

    if responsavel is None:
        raise HTTPException(
            status_code=404,
            detail="Responsavel pelo restaurante nao encontrado",
        )

    return responsavel


def buscar_restaurante(db: Session, id_restaurante: int) -> Restaurante:
    restaurante = (
        db.query(Restaurante)
        .filter(Restaurante.id_restaurante == id_restaurante)
        .first()
    )

    if restaurante is None:
        raise HTTPException(
            status_code=404,
            detail="Restaurante nao encontrado",
        )

    return restaurante


def buscar_restaurante_ativo(db: Session, id_restaurante: int) -> Restaurante:
    restaurante = buscar_restaurante(db, id_restaurante)

    if restaurante.status == RestauranteStatus.INATIVO.value:
        raise HTTPException(
            status_code=400,
            detail="Restaurante inativo",
        )

    return restaurante


def buscar_canal_venda(
    db: Session,
    id_restaurante: int,
    id_canal_venda: int,
) -> CanalVenda:
    canal_venda = (
        db.query(CanalVenda)
        .filter(
            CanalVenda.id_canal_venda == id_canal_venda,
            CanalVenda.id_restaurante == id_restaurante,
        )
        .first()
    )

    if canal_venda is None:
        raise HTTPException(
            status_code=404,
            detail="Canal de venda nao encontrado",
        )

    return canal_venda


def buscar_horario_funcionamento(
    db: Session,
    id_restaurante: int,
    id_horario_funcionamento: int,
) -> HorarioFuncionamento:
    horario_funcionamento = (
        db.query(HorarioFuncionamento)
        .filter(
            HorarioFuncionamento.id_horario_funcionamento
            == id_horario_funcionamento,
            HorarioFuncionamento.id_restaurante == id_restaurante,
        )
        .first()
    )

    if horario_funcionamento is None:
        raise HTTPException(
            status_code=404,
            detail="Horario de funcionamento nao encontrado",
        )

    return horario_funcionamento


def verificar_cnpj_disponivel(db: Session, cnpj: str) -> None:
    restaurante_existente = (
        db.query(Restaurante)
        .filter(Restaurante.cnpj == cnpj)
        .first()
    )

    if restaurante_existente:
        raise HTTPException(
            status_code=400,
            detail="CNPJ ja cadastrado",
        )


def normalizar_cnpj(cnpj: str) -> str:
    cnpj_normalizado = re.sub(r"\D", "", cnpj)

    if not validar_cnpj_digitos(cnpj_normalizado):
        raise HTTPException(
            status_code=400,
            detail="CNPJ invalido",
        )

    return cnpj_normalizado


def restaurante_possui_canal_ativo(restaurante: Restaurante) -> bool:
    return any(canal.ativo for canal in restaurante.canais_venda)


def restaurante_possui_horario(restaurante: Restaurante) -> bool:
    return len(restaurante.horarios_funcionamento) > 0


def validar_restaurante_disponivel(restaurante: Restaurante) -> None:
    if not restaurante_possui_canal_ativo(restaurante):
        raise HTTPException(
            status_code=400,
            detail="Restaurante precisa ter ao menos um canal de venda ativo",
        )

    if not restaurante_possui_horario(restaurante):
        raise HTTPException(
            status_code=400,
            detail="Restaurante precisa ter ao menos um horario de funcionamento",
        )


def validar_intervalo_horario(
    hora_abertura,
    hora_fechamento,
) -> None:
    if hora_abertura >= hora_fechamento:
        raise HTTPException(
            status_code=400,
            detail="Hora de abertura deve ser anterior a hora de fechamento",
        )


def criar_restaurante(
    db: Session,
    restaurante_data: RestauranteCreate,
) -> Restaurante:
    dados_restaurante = (
        restaurante_data.model_dump(
            exclude={
                "categoria_ids",
                "canais_venda",
                "horarios_funcionamento",
            }
        )
    )

    buscar_responsavel(
        db,
        restaurante_data.responsavel_id,
    )

    verificar_cnpj_disponivel(
        db,
        restaurante_data.cnpj,
    )

    buscar_categorias_ativas(
        db,
        restaurante_data.categoria_ids,
    )

    try:
        novo_restaurante = Restaurante(
            **dados_restaurante,
            status=RestauranteStatus.PENDENTE.value,
        )

        novo_restaurante.canais_venda = [
            CanalVenda(
                **canal.model_dump()
            )
            for canal
            in restaurante_data.canais_venda
        ]

        novo_restaurante.horarios_funcionamento = [
            HorarioFuncionamento(
                **horario.model_dump()
            )
            for horario
            in restaurante_data.horarios_funcionamento
        ]

        db.add(novo_restaurante)

        # Gera o id_restaurante sem finalizar
        # a transação.
        db.flush()

        for categoria_id in (
            restaurante_data.categoria_ids
        ):
            vinculo = RestauranteCategoria(
                restaurante_id=(
                    novo_restaurante.id_restaurante
                ),
                categoria_id=categoria_id,
            )

            db.add(vinculo)

        db.commit()
        db.refresh(novo_restaurante)

        return novo_restaurante

    except Exception:
        db.rollback()
        raise


def listar_restaurantes(db: Session) -> list[Restaurante]:
    return db.query(Restaurante).all()


def listar_restaurantes_disponiveis(db: Session) -> list[Restaurante]:
    return (
        db.query(Restaurante)
        .filter(Restaurante.status == RestauranteStatus.DISPONIVEL.value)
        .all()
    )

def listar_horarios_funcionamento(
    db: Session,
    id_restaurante: int,
) -> list[HorarioFuncionamento]:

    buscar_restaurante(
        db,
        id_restaurante,
    )

    return (
        db.query(HorarioFuncionamento)
        .filter(
            HorarioFuncionamento.id_restaurante
            == id_restaurante
        )
        .all()
    )

def buscar_restaurante_por_cnpj(db: Session, cnpj: str) -> Restaurante:
    cnpj = normalizar_cnpj(cnpj)

    restaurante = (
        db.query(Restaurante)
        .filter(Restaurante.cnpj == cnpj)
        .first()
    )

    if restaurante is None:
        raise HTTPException(
            status_code=404,
            detail="Restaurante nao encontrado",
        )

    return restaurante


def buscar_dados_cnpj(db: Session, cnpj: str) -> dict[str, object]:
    restaurante = buscar_restaurante_por_cnpj(db, cnpj)
    responsavel = restaurante.responsavel

    return {
        "id_restaurante": restaurante.id_restaurante,
        "cnpj": restaurante.cnpj,
        "nome_fantasia": restaurante.nome_fantasia,
        "status": restaurante.status,
        "responsavel_email": mascarar_email(responsavel.email),
        "responsavel_celular": mascarar_celular(responsavel.celular),
    }


def atualizar_restaurante(
    db: Session,
    id_restaurante: int,
    restaurante_data: RestauranteUpdate,
) -> Restaurante:

    restaurante = buscar_restaurante(
        db,
        id_restaurante,
    )

    dados = restaurante_data.model_dump(
        exclude_unset=True
    )

    categoria_ids = dados.pop(
        "categoria_ids",
        None,
    )

    try:
        # =========================
        # DADOS DO RESTAURANTE
        # =========================

        for campo, valor in dados.items():
            setattr(
                restaurante,
                campo,
                valor,
            )

        # =========================
        # CATEGORIAS
        # =========================

        if categoria_ids is not None:

            buscar_categorias_ativas(
                db,
                categoria_ids,
            )

            (
                db.query(RestauranteCategoria)
                .filter(
                    RestauranteCategoria.restaurante_id
                    == id_restaurante
                )
                .delete(
                    synchronize_session=False
                )
            )

            for categoria_id in categoria_ids:
                db.add(
                    RestauranteCategoria(
                        restaurante_id=id_restaurante,
                        categoria_id=categoria_id,
                    )
                )

        db.commit()
        db.refresh(restaurante)

        return restaurante

    except Exception:
        db.rollback()
        raise


def deletar_restaurante(
    db: Session,
    id_restaurante: int,
) -> dict[str, str]:
    restaurante = buscar_restaurante(db, id_restaurante)
    restaurante.status = RestauranteStatus.INATIVO.value

    db.commit()

    return {
        "message": "Restaurante desativado com sucesso",
    }


def criar_canal_venda(
    db: Session,
    id_restaurante: int,
    canal_venda_data: CanalVendaCreate,
) -> CanalVenda:

    restaurante = buscar_restaurante_ativo(
        db,
        id_restaurante,
    )

    canal_existente = (
        db.query(CanalVenda)
        .filter(
            CanalVenda.id_restaurante == id_restaurante,
            CanalVenda.tipo == canal_venda_data.tipo,
        )
        .first()
    )

    if canal_existente:
        raise HTTPException(
            status_code=400,
            detail="Canal de venda ja cadastrado para este restaurante",
        )

    canal_venda = CanalVenda(
        id_restaurante=restaurante.id_restaurante,
        **canal_venda_data.model_dump(),
    )

    try:
        db.add(canal_venda)
        db.commit()
        db.refresh(canal_venda)

        atualizar_status_restaurante(
            db,
            id_restaurante,
        )

        return canal_venda

    except Exception:
        db.rollback()
        raise

def listar_canais_venda(
    db: Session,
    id_restaurante: int,
) -> list[CanalVenda]:
    buscar_restaurante(db, id_restaurante)

    return (
        db.query(CanalVenda)
        .filter(CanalVenda.id_restaurante == id_restaurante)
        .all()
    )


def atualizar_canal_venda(
    db: Session,
    id_restaurante: int,
    id_canal_venda: int,
    canal_venda_data: CanalVendaUpdate,
) -> CanalVenda:

    buscar_restaurante_ativo(
        db,
        id_restaurante,
    )

    canal_venda = buscar_canal_venda(
        db,
        id_restaurante,
        id_canal_venda,
    )

    dados_atualizados = (
        canal_venda_data.model_dump(
            exclude_unset=True
        )
    )

    for campo in CAMPOS_CANAL_VENDA_OBRIGATORIOS:
        if (
            campo in dados_atualizados
            and dados_atualizados[campo] is None
        ):
            raise HTTPException(
                status_code=400,
                detail=f"{campo} nao pode ser nulo",
            )

    if (
        "tipo" in dados_atualizados
        and dados_atualizados["tipo"]
        != canal_venda.tipo
    ):
        canal_existente = (
            db.query(CanalVenda)
            .filter(
                CanalVenda.id_restaurante
                == id_restaurante,

                CanalVenda.tipo
                == dados_atualizados["tipo"],
            )
            .first()
        )

        if canal_existente:
            raise HTTPException(
                status_code=400,
                detail="Canal de venda ja cadastrado para este restaurante",
            )

    try:
        for campo, valor in dados_atualizados.items():
            setattr(
                canal_venda,
                campo,
                valor,
            )

        db.commit()
        db.refresh(canal_venda)

        atualizar_status_restaurante(
            db,
            id_restaurante,
        )

        return canal_venda

    except Exception:
        db.rollback()
        raise

def deletar_canal_venda(
    db: Session,
    id_restaurante: int,
    id_canal_venda: int,
) -> dict[str, str]:

    buscar_restaurante_ativo(
        db,
        id_restaurante,
    )

    canal_venda = buscar_canal_venda(
        db,
        id_restaurante,
        id_canal_venda,
    )

    try:
        canal_venda.ativo = False

        db.commit()

        atualizar_status_restaurante(
            db,
            id_restaurante,
        )

        return {
            "message":
                "Canal de venda desativado com sucesso",
        }

    except Exception:
        db.rollback()
        raise

def criar_horario_funcionamento(
    db: Session,
    id_restaurante: int,
    horario_data: HorarioFuncionamentoCreate,
) -> HorarioFuncionamento:

    restaurante = buscar_restaurante_ativo(
        db,
        id_restaurante,
    )

    horario_funcionamento = HorarioFuncionamento(
        id_restaurante=restaurante.id_restaurante,
        **horario_data.model_dump(),
    )

    try:
        db.add(
            horario_funcionamento
        )

        db.commit()

        db.refresh(
            horario_funcionamento
        )

        atualizar_status_restaurante(
            db,
            id_restaurante,
        )

        return horario_funcionamento

    except Exception:
        db.rollback()
        raise


def atualizar_horario_funcionamento(
    db: Session,
    id_restaurante: int,
    id_horario_funcionamento: int,
    horario_data: HorarioFuncionamentoUpdate,
) -> HorarioFuncionamento:

    buscar_restaurante_ativo(
        db,
        id_restaurante,
    )

    horario_funcionamento = (
        buscar_horario_funcionamento(
            db,
            id_restaurante,
            id_horario_funcionamento,
        )
    )

    dados_atualizados = (
        horario_data.model_dump(
            exclude_unset=True
        )
    )

    for campo in CAMPOS_HORARIO_FUNCIONAMENTO_OBRIGATORIOS:
        if (
            campo in dados_atualizados
            and dados_atualizados[campo] is None
        ):
            raise HTTPException(
                status_code=400,
                detail=f"{campo} nao pode ser nulo",
            )

    try:
        for campo, valor in dados_atualizados.items():
            setattr(
                horario_funcionamento,
                campo,
                valor,
            )

        validar_intervalo_horario(
            horario_funcionamento.hora_abertura,
            horario_funcionamento.hora_fechamento,
        )

        db.commit()

        db.refresh(
            horario_funcionamento
        )

        atualizar_status_restaurante(
            db,
            id_restaurante,
        )

        return horario_funcionamento

    except Exception:
        db.rollback()
        raise


def deletar_horario_funcionamento(
    db: Session,
    id_restaurante: int,
    id_horario_funcionamento: int,
) -> dict[str, str]:

    buscar_restaurante_ativo(
        db,
        id_restaurante,
    )

    horario_funcionamento = (
        buscar_horario_funcionamento(
            db,
            id_restaurante,
            id_horario_funcionamento,
        )
    )

    try:
        db.delete(
            horario_funcionamento
        )

        db.commit()

        atualizar_status_restaurante(
            db,
            id_restaurante,
        )

        return {
            "message":
                "Horario de funcionamento excluido com sucesso",
        }

    except Exception:
        db.rollback()
        raise

def mascarar_email(email: str) -> str:
    usuario, dominio = email.split("@", maxsplit=1)

    if len(usuario) <= 2:
        return f"{usuario[0]}****@{dominio}"

    return f"{usuario[:2]}****{usuario[-1]}@{dominio}"


def mascarar_celular(celular: str) -> str:
    digitos = "".join(caractere for caractere in celular if caractere.isdigit())

    if len(digitos) <= 6:
        return "****"

    return f"{digitos[:2]}*****{digitos[-4:]}"

def buscar_categorias_ativas(
    db: Session,
    categoria_ids: list[int],
) -> list[Categorias_restaurante]:
    categorias = (
        db.query(Categorias_restaurante)
        .filter(
            Categorias_restaurante.id.in_(
                categoria_ids
            ),
            Categorias_restaurante.status
            == "ATIVA",
        )
        .all()
    )

    ids_encontrados = {
        categoria.id
        for categoria in categorias
    }

    ids_solicitados = set(categoria_ids)

    ids_invalidos = (
        ids_solicitados - ids_encontrados
    )

    if ids_invalidos:
        raise HTTPException(
            status_code=400,
            detail=(
                "Uma ou mais categorias nao existem "
                "ou estao inativas"
            ),
        )

    return categorias

def atualizar_status_restaurante(
    db: Session,
    id_restaurante: int,
) -> Restaurante:
    restaurante = buscar_restaurante(
        db,
        id_restaurante,
    )

    possui_canal_venda = (
        db.query(CanalVenda)
        .filter(
            CanalVenda.id_restaurante == id_restaurante,
            CanalVenda.ativo.is_(True),
        )
        .first()
        is not None
    )

    possui_horario = (
        db.query(HorarioFuncionamento)
        .filter(
            HorarioFuncionamento.id_restaurante == id_restaurante
        )
        .first()
        is not None
    )

    possui_endereco = (
        db.query(EnderecoRestaurante)
        .filter(
            EnderecoRestaurante.id_restaurante == id_restaurante
        )
        .first()
        is not None
    )

    if (
        possui_canal_venda
        and possui_horario
        and possui_endereco
    ):
        restaurante.status = (
            RestauranteStatus.DISPONIVEL.value
        )
    else:
        restaurante.status = (
            RestauranteStatus.PENDENTE.value
        )

    db.commit()
    db.refresh(restaurante)

    return restaurante

def verificar_status_cadastro(
    db: Session,
    id_restaurante: int,
):
    restaurante = buscar_restaurante(
        db,
        id_restaurante,
    )

    possui_canal_venda = (
        db.query(CanalVenda)
        .filter(
            CanalVenda.id_restaurante == id_restaurante,
            CanalVenda.ativo.is_(True),
        )
        .first()
        is not None
    )

    possui_horario = (
        db.query(HorarioFuncionamento)
        .filter(
            HorarioFuncionamento.id_restaurante == id_restaurante,
        )
        .first()
        is not None
    )

    possui_endereco = (
        db.query(EnderecoRestaurante)
        .filter(
            EnderecoRestaurante.id_restaurante == id_restaurante,
        )
        .first()
        is not None
    )

    completo = (
        possui_canal_venda
        and possui_horario
        and possui_endereco
    )

    if completo:
        restaurante.status = (
            RestauranteStatus.DISPONIVEL.value
        )
    else:
        restaurante.status = (
            RestauranteStatus.PENDENTE.value
        )

    db.commit()
    db.refresh(restaurante)

    proxima_etapa = None

    if not possui_canal_venda:
        proxima_etapa = "canais-venda"

    elif not possui_horario:
        proxima_etapa = "horarios-funcionamento"

    elif not possui_endereco:
        proxima_etapa = "endereco"

    return {
        "id_restaurante": restaurante.id_restaurante,
        "status": restaurante.status,
        "completo": completo,
        "possui_canal_venda": possui_canal_venda,
        "possui_horario": possui_horario,
        "possui_endereco": possui_endereco,
        "proxima_etapa": proxima_etapa,
    }


def verificar_funcionamento_restaurante(
    db: Session,
    id_restaurante: int,
) -> dict[str, object]:

    buscar_restaurante(
        db,
        id_restaurante,
    )

    agora = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    )

    hora_atual = agora.time()

    dias_semana = {
        0: "SEGUNDA",
        1: "TERCA",
        2: "QUARTA",
        3: "QUINTA",
        4: "SEXTA",
        5: "SABADO",
        6: "DOMINGO",
    }

    dia_atual = dias_semana[
        agora.weekday()
    ]

    horarios_hoje = (
        db.query(HorarioFuncionamento)
        .filter(
            HorarioFuncionamento.id_restaurante
            == id_restaurante,
            HorarioFuncionamento.dia_semana
            == dia_atual,
        )
        .order_by(
            HorarioFuncionamento.hora_abertura
        )
        .all()
    )

    # =========================
    # VERIFICA SE ESTÁ ABERTO
    # =========================

    for horario in horarios_hoje:

        if (
            horario.hora_abertura
            <= hora_atual
            < horario.hora_fechamento
        ):
            return {
                "aberto": True,
                "mensagem": "Aberto agora",
                "dia_semana": dia_atual,
                "hora_atual": hora_atual.strftime(
                    "%H:%M"
                ),
                "abre_as": None,
                "fecha_as":
                    horario.hora_fechamento.strftime(
                        "%H:%M"
                    ),
                "proximo_dia": None,
                "proximo_evento":
                    f"Fecha às "
                    f"{horario.hora_fechamento.strftime('%H:%M')}",
            }

    # =========================
    # VERIFICA SE ABRE
    # NOVAMENTE HOJE
    # =========================

    for horario in horarios_hoje:

        if (
            horario.hora_abertura
            > hora_atual
        ):
            return {
                "aberto": False,
                "mensagem": "Fechado agora",
                "dia_semana": dia_atual,
                "hora_atual": hora_atual.strftime(
                    "%H:%M"
                ),
                "abre_as":
                    horario.hora_abertura.strftime(
                        "%H:%M"
                    ),
                "fecha_as": None,
                "proximo_dia": dia_atual,
                "proximo_evento":
                    f"Reabre hoje às "
                    f"{horario.hora_abertura.strftime('%H:%M')}",
            }

    # =========================
    # PROCURA PRÓXIMO DIA
    # =========================

    for quantidade_dias in range(
        1,
        8,
    ):
        indice_dia = (
            agora.weekday()
            + quantidade_dias
        ) % 7

        proximo_dia = dias_semana[
            indice_dia
        ]

        proximo_horario = (
            db.query(
                HorarioFuncionamento
            )
            .filter(
                HorarioFuncionamento.id_restaurante
                == id_restaurante,
                HorarioFuncionamento.dia_semana
                == proximo_dia,
            )
            .order_by(
                HorarioFuncionamento.hora_abertura
            )
            .first()
        )

        if proximo_horario:

            if quantidade_dias == 1:
                texto_dia = "amanhã"

            else:
                nomes_dias = {
                    "SEGUNDA": "segunda-feira",
                    "TERCA": "terça-feira",
                    "QUARTA": "quarta-feira",
                    "QUINTA": "quinta-feira",
                    "SEXTA": "sexta-feira",
                    "SABADO": "sábado",
                    "DOMINGO": "domingo",
                }

                texto_dia = nomes_dias[
                    proximo_dia
                ]

            return {
                "aberto": False,
                "mensagem": "Fechado agora",
                "dia_semana": dia_atual,
                "hora_atual": hora_atual.strftime(
                    "%H:%M"
                ),
                "abre_as":
                    proximo_horario.hora_abertura.strftime(
                        "%H:%M"
                    ),
                "fecha_as": None,
                "proximo_dia":
                    proximo_dia,
                "proximo_evento":
                    f"Abre {texto_dia} às "
                    f"{proximo_horario.hora_abertura.strftime('%H:%M')}",
            }

    # =========================
    # SEM HORÁRIOS CADASTRADOS
    # =========================

    return {
        "aberto": False,
        "mensagem": "Fechado agora",
        "dia_semana": dia_atual,
        "hora_atual": hora_atual.strftime(
            "%H:%M"
        ),
        "abre_as": None,
        "fecha_as": None,
        "proximo_dia": None,
        "proximo_evento":
            "Nenhum horário de funcionamento cadastrado",
    }
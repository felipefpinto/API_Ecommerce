import re

from fastapi import HTTPException
from sqlalchemy.orm import Session

from api_ecommerce.models import (
    CanalVenda,
    HorarioFuncionamento,
    Restaurante,
    Usuario,
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
    "categoria",
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


def buscar_usuario(db: Session, id_usuario: int) -> Usuario:
    usuario = (
        db.query(Usuario)
        .filter(Usuario.id_usuario == id_usuario)
        .first()
    )

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario responsavel nao encontrado",
        )

    return usuario


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
    dados_restaurante = restaurante_data.model_dump(
        exclude={
            "canais_venda",
            "horarios_funcionamento",
        }
    )

    buscar_usuario(db, restaurante_data.responsavel_usuario_id)
    verificar_cnpj_disponivel(db, restaurante_data.cnpj)

    novo_restaurante = Restaurante(
        **dados_restaurante,
        status=RestauranteStatus.PENDENTE.value,
    )

    novo_restaurante.canais_venda = [
        CanalVenda(**canal.model_dump())
        for canal in restaurante_data.canais_venda
    ]
    novo_restaurante.horarios_funcionamento = [
        HorarioFuncionamento(**horario.model_dump())
        for horario in restaurante_data.horarios_funcionamento
    ]

    db.add(novo_restaurante)
    db.commit()
    db.refresh(novo_restaurante)

    return novo_restaurante


def listar_restaurantes(db: Session) -> list[Restaurante]:
    return db.query(Restaurante).all()


def listar_restaurantes_disponiveis(db: Session) -> list[Restaurante]:
    return (
        db.query(Restaurante)
        .filter(Restaurante.status == RestauranteStatus.DISPONIVEL.value)
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
    restaurante = buscar_restaurante(db, id_restaurante)
    dados_atualizados = restaurante_data.model_dump(exclude_unset=True)

    for campo in CAMPOS_RESTAURANTE_OBRIGATORIOS:
        if campo in dados_atualizados and dados_atualizados[campo] is None:
            raise HTTPException(
                status_code=400,
                detail=f"{campo} nao pode ser nulo",
            )

    for campo, valor in dados_atualizados.items():
        setattr(restaurante, campo, valor)

    if restaurante.status == RestauranteStatus.DISPONIVEL.value:
        validar_restaurante_disponivel(restaurante)

    db.commit()
    db.refresh(restaurante)

    return restaurante


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
    restaurante = buscar_restaurante_ativo(db, id_restaurante)

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

    db.add(canal_venda)
    db.commit()
    db.refresh(canal_venda)

    return canal_venda


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
    restaurante = buscar_restaurante_ativo(db, id_restaurante)
    canal_venda = buscar_canal_venda(db, id_restaurante, id_canal_venda)
    dados_atualizados = canal_venda_data.model_dump(exclude_unset=True)

    for campo in CAMPOS_CANAL_VENDA_OBRIGATORIOS:
        if campo in dados_atualizados and dados_atualizados[campo] is None:
            raise HTTPException(
                status_code=400,
                detail=f"{campo} nao pode ser nulo",
            )

    if "tipo" in dados_atualizados and dados_atualizados["tipo"] != canal_venda.tipo:
        canal_existente = (
            db.query(CanalVenda)
            .filter(
                CanalVenda.id_restaurante == id_restaurante,
                CanalVenda.tipo == dados_atualizados["tipo"],
            )
            .first()
        )

        if canal_existente:
            raise HTTPException(
                status_code=400,
                detail="Canal de venda ja cadastrado para este restaurante",
            )

    for campo, valor in dados_atualizados.items():
        setattr(canal_venda, campo, valor)

    if restaurante.status == RestauranteStatus.DISPONIVEL.value:
        validar_restaurante_disponivel(restaurante)

    db.commit()
    db.refresh(canal_venda)

    return canal_venda


def deletar_canal_venda(
    db: Session,
    id_restaurante: int,
    id_canal_venda: int,
) -> dict[str, str]:
    restaurante = buscar_restaurante_ativo(db, id_restaurante)
    canal_venda = buscar_canal_venda(db, id_restaurante, id_canal_venda)
    canal_venda.ativo = False

    if restaurante.status == RestauranteStatus.DISPONIVEL.value:
        validar_restaurante_disponivel(restaurante)

    db.commit()

    return {
        "message": "Canal de venda desativado com sucesso",
    }


def criar_horario_funcionamento(
    db: Session,
    id_restaurante: int,
    horario_data: HorarioFuncionamentoCreate,
) -> HorarioFuncionamento:
    restaurante = buscar_restaurante_ativo(db, id_restaurante)

    horario_funcionamento = HorarioFuncionamento(
        id_restaurante=restaurante.id_restaurante,
        **horario_data.model_dump(),
    )

    db.add(horario_funcionamento)
    db.commit()
    db.refresh(horario_funcionamento)

    return horario_funcionamento


def listar_horarios_funcionamento(
    db: Session,
    id_restaurante: int,
) -> list[HorarioFuncionamento]:
    buscar_restaurante(db, id_restaurante)

    return (
        db.query(HorarioFuncionamento)
        .filter(HorarioFuncionamento.id_restaurante == id_restaurante)
        .all()
    )


def atualizar_horario_funcionamento(
    db: Session,
    id_restaurante: int,
    id_horario_funcionamento: int,
    horario_data: HorarioFuncionamentoUpdate,
) -> HorarioFuncionamento:
    buscar_restaurante_ativo(db, id_restaurante)
    horario_funcionamento = buscar_horario_funcionamento(
        db,
        id_restaurante,
        id_horario_funcionamento,
    )
    dados_atualizados = horario_data.model_dump(exclude_unset=True)

    for campo in CAMPOS_HORARIO_FUNCIONAMENTO_OBRIGATORIOS:
        if campo in dados_atualizados and dados_atualizados[campo] is None:
            raise HTTPException(
                status_code=400,
                detail=f"{campo} nao pode ser nulo",
            )

    for campo, valor in dados_atualizados.items():
        setattr(horario_funcionamento, campo, valor)

    validar_intervalo_horario(
        horario_funcionamento.hora_abertura,
        horario_funcionamento.hora_fechamento,
    )

    db.commit()
    db.refresh(horario_funcionamento)

    return horario_funcionamento


def deletar_horario_funcionamento(
    db: Session,
    id_restaurante: int,
    id_horario_funcionamento: int,
) -> dict[str, str]:
    restaurante = buscar_restaurante_ativo(db, id_restaurante)
    horario_funcionamento = buscar_horario_funcionamento(
        db,
        id_restaurante,
        id_horario_funcionamento,
    )

    if (
        restaurante.status == RestauranteStatus.DISPONIVEL.value
        and len(restaurante.horarios_funcionamento) <= 1
    ):
        raise HTTPException(
            status_code=400,
            detail="Restaurante disponivel precisa ter ao menos um horario",
        )

    db.delete(horario_funcionamento)
    db.commit()

    return {
        "message": "Horario de funcionamento excluido com sucesso",
    }


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

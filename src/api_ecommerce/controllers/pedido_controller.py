from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from api_ecommerce.models.carrinho import (
    Carrinho,
    CarrinhoItem,
)
from api_ecommerce.models.complemento import Complemento
from api_ecommerce.models.configuracao_entrega import ConfiguracaoEntrega
from api_ecommerce.models.endereco import Endereco
from api_ecommerce.models.pedido import (
    Pedido,
    ItemPedido,
    ItemPedidoComplemento,
)
from api_ecommerce.models.produto import Produto
from api_ecommerce.models.restaurante import Restaurante
from api_ecommerce.models.usuario import Usuario
from api_ecommerce.schemas.pedido import PedidoCreate
from api_ecommerce.services.entrega_service import calcular_entrega


# =========================================================
# BUSCAR PEDIDO COMPLETO
# =========================================================

def buscar_pedido_por_id(
    db: Session,
    id_pedido: int,
) -> Pedido:

    stmt = (
        select(Pedido)
        .where(Pedido.id_pedido == id_pedido)
        .options(
            selectinload(Pedido.itens)
            .selectinload(ItemPedido.complementos),
            selectinload(Pedido.pagamentos),
        )
    )

    pedido = db.scalar(stmt)

    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado.",
        )

    return pedido


# =========================================================
# BUSCAR CARRINHO ATIVO COMPLETO
# =========================================================

def buscar_carrinho_ativo(
    db: Session,
    id_usuario: int,
) -> Carrinho:

    stmt = (
        select(Carrinho)
        .where(
            Carrinho.id_usuario == id_usuario,
            Carrinho.status == "ATIVO",
        )
        .options(
            selectinload(Carrinho.itens)
            .selectinload(CarrinhoItem.complementos)
        )
    )

    carrinho = db.scalar(stmt)

    if not carrinho:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="O usuário não possui carrinho ativo.",
        )

    if not carrinho.itens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O carrinho está vazio.",
        )

    return carrinho


# =========================================================
# CALCULAR SUBTOTAL
# =========================================================

def calcular_subtotal_carrinho(
    carrinho: Carrinho,
) -> Decimal:

    subtotal = Decimal("0.00")

    for item in carrinho.itens:

        valor_complementos = Decimal("0.00")

        for complemento in item.complementos:
            valor_complementos += (
                complemento.preco_unitario
                * complemento.quantidade
            )

        valor_unitario_completo = (
            item.preco_unitario
            + valor_complementos
        )

        subtotal += (
            valor_unitario_completo
            * item.quantidade
        )

    return subtotal


# =========================================================
# CRIAR PEDIDO
# =========================================================

def criar_pedido(
    db: Session,
    id_usuario: int,
    dados: PedidoCreate,
) -> Pedido:

    # -----------------------------------------------------
    # 1. Valida usuário
    # -----------------------------------------------------

    usuario = db.get(
        Usuario,
        id_usuario,
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    # -----------------------------------------------------
    # 2. Busca carrinho
    # -----------------------------------------------------

    carrinho = buscar_carrinho_ativo(
        db=db,
        id_usuario=id_usuario,
    )

    # -----------------------------------------------------
    # 3. Valida restaurante
    # -----------------------------------------------------

    restaurante = db.get(
        Restaurante,
        carrinho.id_restaurante,
    )

    if not restaurante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurante não encontrado.",
        )

    # -----------------------------------------------------
    # 4. Normaliza tipo de entrega
    # -----------------------------------------------------

    tipo_entrega = dados.tipo_entrega.strip().upper()

    if tipo_entrega not in {
        "ENTREGA",
        "RETIRADA",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Tipo de entrega inválido. "
                "Utilize ENTREGA ou RETIRADA."
            ),
        )

    # -----------------------------------------------------
    # 5. Calcula subtotal
    # -----------------------------------------------------

    subtotal = calcular_subtotal_carrinho(
        carrinho
    )

    # -----------------------------------------------------
    # 6. Dados iniciais da entrega
    # -----------------------------------------------------

    taxa_entrega = Decimal("0.00")
    endereco = None

    # -----------------------------------------------------
    # 7. Valida entrega
    # -----------------------------------------------------

    if tipo_entrega == "ENTREGA":

        if dados.id_endereco is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "O endereço é obrigatório "
                    "para pedidos de entrega."
                ),
            )

        endereco = db.get(
            Endereco,
            dados.id_endereco,
        )

        if not endereco:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endereço não encontrado.",
            )

        # Impede usar endereço de outro usuário
        if endereco.id_usuario != id_usuario:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Este endereço não pertence "
                    "ao usuário."
                ),
            )

        entrega = calcular_entrega(
            db=db,
            id_restaurante=carrinho.id_restaurante,
            id_endereco=endereco.id_endereco,
        )

        if not entrega["dentro_area_entrega"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "O endereço está fora da "
                    "área de entrega do restaurante."
                ),
            )

        if entrega["taxa_entrega"] is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Não existe uma faixa de entrega "
                    "configurada para este endereço."
                ),
            )

        valor_minimo = Decimal(
            str(entrega["valor_minimo_pedido"])
        )

        if subtotal < valor_minimo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"O pedido mínimo deste restaurante "
                    f"é R$ {valor_minimo:.2f}."
                ),
            )

        taxa_entrega = Decimal(
            str(entrega["taxa_entrega"])
        )

        # ---------------------------------------------
        # Regra de entrega grátis
        # ---------------------------------------------

        configuracao = (
            db.query(ConfiguracaoEntrega)
            .filter(
                ConfiguracaoEntrega.id_restaurante
                == carrinho.id_restaurante,
                ConfiguracaoEntrega.ativo.is_(True),
            )
            .first()
        )

        if (
            configuracao
            and configuracao.entrega_gratis
        ):
            minimo_gratis = (
                configuracao
                .valor_minimo_entrega_gratis
            )

            if (
                minimo_gratis is None
                or subtotal >= minimo_gratis
            ):
                taxa_entrega = Decimal("0.00")

    # -----------------------------------------------------
    # 8. RETIRADA não usa endereço
    # -----------------------------------------------------

    else:
        endereco = None
        taxa_entrega = Decimal("0.00")

    # -----------------------------------------------------
    # 9. Desconto
    # -----------------------------------------------------

    desconto = Decimal("0.00")

    # -----------------------------------------------------
    # 10. Total
    # -----------------------------------------------------

    valor_total = (
        subtotal
        + taxa_entrega
        - desconto
    )

    # -----------------------------------------------------
    # 11. Cria pedido
    # -----------------------------------------------------

    pedido = Pedido(
        id_usuario=id_usuario,
        id_restaurante=carrinho.id_restaurante,

        id_endereco=(
            endereco.id_endereco
            if endereco
            else None
        ),

        status="AGUARDANDO_PAGAMENTO",
        tipo_entrega=tipo_entrega,

        subtotal=subtotal,
        taxa_entrega=taxa_entrega,
        desconto=desconto,
        valor_total=valor_total,

        observacao=dados.observacao,

        endereco_cep=(
            endereco.cep
            if endereco
            else None
        ),

        endereco_logradouro=(
            endereco.logradouro
            if endereco
            else None
        ),

        endereco_numero=(
            endereco.numero
            if endereco
            else None
        ),

        endereco_complemento=(
            endereco.complemento
            if endereco
            else None
        ),

        endereco_bairro=(
            endereco.bairro
            if endereco
            else None
        ),

        endereco_cidade=(
            endereco.cidade
            if endereco
            else None
        ),

        endereco_uf=(
            endereco.uf
            if endereco
            else None
        ),

        endereco_ponto_referencia=(
            endereco.ponto_referencia
            if endereco
            else None
        ),
    )

    try:
        db.add(pedido)
        db.flush()

        # -------------------------------------------------
        # 12. Copia os itens do carrinho
        # -------------------------------------------------

        for item_carrinho in carrinho.itens:

            produto = db.get(
                Produto,
                item_carrinho.id_produto,
            )

            if not produto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"Produto "
                        f"{item_carrinho.id_produto} "
                        f"não encontrado."
                    ),
                )

            # ---------------------------------------------
            # Soma complementos daquele item
            # ---------------------------------------------

            total_complementos_unitario = Decimal("0.00")

            for comp in item_carrinho.complementos:
                total_complementos_unitario += (
                    comp.preco_unitario
                    * comp.quantidade
                )

            subtotal_item = (
                item_carrinho.preco_unitario
                + total_complementos_unitario
            ) * item_carrinho.quantidade

            item_pedido = ItemPedido(
                id_pedido=pedido.id_pedido,
                id_produto=produto.id_produto,

                nome_produto=produto.nome,

                quantidade=item_carrinho.quantidade,

                preco_unitario=(
                    item_carrinho.preco_unitario
                ),

                subtotal=subtotal_item,

                observacao=item_carrinho.observacao,
            )

            db.add(item_pedido)
            db.flush()

            # ---------------------------------------------
            # 13. Copia complementos
            # ---------------------------------------------

            for comp_carrinho in item_carrinho.complementos:

                complemento = db.get(
                    Complemento,
                    comp_carrinho.id_complemento,
                )

                if not complemento:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=(
                            "Complemento "
                            f"{comp_carrinho.id_complemento} "
                            "não encontrado."
                        ),
                    )

                subtotal_complemento = (
                    comp_carrinho.preco_unitario
                    * comp_carrinho.quantidade
                )

                item_complemento = ItemPedidoComplemento(
                    id_item_pedido=(
                        item_pedido.id_item_pedido
                    ),

                    id_complemento=(
                        complemento.id_complemento
                    ),

                    nome_complemento=(
                        complemento.nome
                    ),

                    quantidade=(
                        comp_carrinho.quantidade
                    ),

                    preco_unitario=(
                        comp_carrinho.preco_unitario
                    ),

                    subtotal=subtotal_complemento,
                )

                db.add(item_complemento)

        # -------------------------------------------------
        # 14. Encerra carrinho
        # -------------------------------------------------

        carrinho.status = "FINALIZADO"

        # -------------------------------------------------
        # 15. Salva tudo
        # -------------------------------------------------

        db.commit()

    except Exception:
        db.rollback()
        raise

    # -----------------------------------------------------
    # 16. Retorna pedido completo
    # -----------------------------------------------------

    return buscar_pedido_por_id(
        db=db,
        id_pedido=pedido.id_pedido,
    )


# =========================================================
# LISTAR PEDIDOS DO USUÁRIO
# =========================================================

def listar_pedidos_usuario(
    db: Session,
    id_usuario: int,
) -> list[Pedido]:

    # -----------------------------------------------------
    # 1. Valida usuário
    # -----------------------------------------------------

    usuario = db.get(
        Usuario,
        id_usuario,
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    # -----------------------------------------------------
    # 2. Busca pedidos
    # -----------------------------------------------------

    stmt = (
        select(Pedido)
        .where(
            Pedido.id_usuario == id_usuario
        )
        .options(
            selectinload(Pedido.itens)
            .selectinload(ItemPedido.complementos),
            selectinload(Pedido.pagamentos),
        )
        .order_by(
            Pedido.created_at.desc()
        )
    )

    pedidos = db.scalars(stmt).all()

    for pedido in pedidos:
        restaurante = db.get(
            Restaurante,
            pedido.id_restaurante,
        )

        if restaurante:
            pedido.nome_restaurante = restaurante.nome_fantasia
            pedido.logo_restaurante = restaurante.logo_url

    return list(pedidos)

# =========================================================
# BUSCAR PEDIDO DO USUÁRIO
# =========================================================

def buscar_pedido_usuario(
    db: Session,
    id_usuario: int,
    id_pedido: int,
) -> Pedido:

    # -----------------------------------------------------
    # 1. Valida usuário
    # -----------------------------------------------------

    usuario = db.get(
        Usuario,
        id_usuario,
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    # -----------------------------------------------------
    # 2. Busca pedido completo
    # -----------------------------------------------------

    pedido = buscar_pedido_por_id(
        db=db,
        id_pedido=id_pedido,
    )

    # -----------------------------------------------------
    # 3. Verifica se o pedido pertence ao usuário
    # -----------------------------------------------------

    if pedido.id_usuario != id_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado para este usuário.",
        )

    return pedido

# =========================================================
# LISTAR PEDIDOS DO RESTAURANTE
# =========================================================

def listar_pedidos_restaurante(
    db: Session,
    id_restaurante: int,
) -> list[Pedido]:

    # -----------------------------------------------------
    # 1. Valida restaurante
    # -----------------------------------------------------

    restaurante = db.get(
        Restaurante,
        id_restaurante,
    )

    if not restaurante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurante não encontrado.",
        )

    # -----------------------------------------------------
    # 2. Busca pedidos
    # -----------------------------------------------------

    stmt = (
        select(Pedido)
        .where(
            Pedido.id_restaurante == id_restaurante
        )
        .options(
            selectinload(Pedido.itens)
            .selectinload(ItemPedido.complementos),
            selectinload(Pedido.pagamentos),
        )
        .order_by(
            Pedido.created_at.desc()
        )
    )

    pedidos = db.scalars(stmt).all()

    return list(pedidos)

# =========================================================
# BUSCAR PEDIDO DO RESTAURANTE
# =========================================================

def buscar_pedido_restaurante(
    db: Session,
    id_restaurante: int,
    id_pedido: int,
) -> Pedido:

    # Valida restaurante
    restaurante = db.get(
        Restaurante,
        id_restaurante,
    )

    if not restaurante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurante não encontrado.",
        )

    # Busca pedido completo
    pedido = buscar_pedido_por_id(
        db=db,
        id_pedido=id_pedido,
    )

    # Garante que o pedido pertence ao restaurante
    if pedido.id_restaurante != id_restaurante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado para este restaurante.",
        )

    return pedido

TRANSICOES_STATUS = {
    "ACEITO": {
        "EM_PREPARO",
    },
    "EM_PREPARO": {
        "PRONTO",
    },
    "PRONTO": {
        "SAIU_PARA_ENTREGA",
    },
    "SAIU_PARA_ENTREGA": {
        "ENTREGUE",
    },
}

# =========================================================
# ATUALIZAR STATUS DO PEDIDO
# =========================================================

def atualizar_status_pedido(
    db: Session,
    id_restaurante: int,
    id_pedido: int,
    novo_status: str,
) -> Pedido:

    pedido = buscar_pedido_restaurante(
        db=db,
        id_restaurante=id_restaurante,
        id_pedido=id_pedido,
    )

    status_atual = pedido.status

    # O fluxo muda de acordo com o tipo de entrega.
    if pedido.tipo_entrega == "RETIRADA":
        transicoes_permitidas = {
            "ACEITO": {"EM_PREPARO"},
            "EM_PREPARO": {"PRONTO"},
            "PRONTO": {"ENTREGUE"},
        }
    else:
        transicoes_permitidas = {
            "ACEITO": {"EM_PREPARO"},
            "EM_PREPARO": {"PRONTO"},
            "PRONTO": {"SAIU_PARA_ENTREGA"},
            "SAIU_PARA_ENTREGA": {"ENTREGUE"},
        }

    permitidos = transicoes_permitidas.get(
        status_atual,
        set(),
    )

    if novo_status not in permitidos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Não é possível alterar o pedido "
                f"de {status_atual} para {novo_status}."
            ),
        )

    try:
        pedido.status = novo_status

        db.commit()
        db.refresh(pedido)

    except Exception:
        db.rollback()
        raise

    return buscar_pedido_por_id(
        db=db,
        id_pedido=id_pedido,
    )

# =========================================================
# ACEITAR PEDIDO
# =========================================================

def aceitar_pedido(
    db: Session,
    id_restaurante: int,
    id_pedido: int,
) -> Pedido:

    pedido = buscar_pedido_restaurante(
        db=db,
        id_restaurante=id_restaurante,
        id_pedido=id_pedido,
    )

    if pedido.status != "AGUARDANDO_ACEITE":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "O pedido só pode ser aceito quando "
                "estiver aguardando aceite."
            ),
        )

    try:
        pedido.status = "ACEITO"

        db.commit()
        db.refresh(pedido)

    except Exception:
        db.rollback()
        raise

    return buscar_pedido_por_id(
        db=db,
        id_pedido=id_pedido,
    )


# =========================================================
# RECUSAR PEDIDO
# =========================================================

def recusar_pedido(
    db: Session,
    id_restaurante: int,
    id_pedido: int,
) -> Pedido:

    pedido = buscar_pedido_restaurante(
        db=db,
        id_restaurante=id_restaurante,
        id_pedido=id_pedido,
    )

    if pedido.status != "AGUARDANDO_ACEITE":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "O pedido só pode ser recusado quando "
                "estiver aguardando aceite."
            ),
        )

    try:
        pedido.status = "RECUSADO"

        db.commit()
        db.refresh(pedido)

    except Exception:
        db.rollback()
        raise

    return buscar_pedido_por_id(
        db=db,
        id_pedido=id_pedido,
    )
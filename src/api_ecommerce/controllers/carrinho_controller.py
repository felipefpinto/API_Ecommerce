from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from api_ecommerce.models.carrinho import (
    Carrinho,
    CarrinhoItem,
    CarrinhoItemComplemento,
)
from api_ecommerce.models.complemento import Complemento
from api_ecommerce.models.produto import Produto
from api_ecommerce.models.restaurante import Restaurante
from api_ecommerce.models.produto_grupo_complemento import (
    ProdutoGrupoComplemento,
)
from api_ecommerce.schemas.carrinho import CarrinhoAdicionarItem


# =========================================================
# BUSCAR CARRINHO ATIVO
# =========================================================

def buscar_carrinho_ativo(
    db: Session,
    id_usuario: int,
) -> Carrinho | None:

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
        return None

    # =====================================================
    # RESTAURANTE
    # =====================================================

    restaurante = db.get(
        Restaurante,
        carrinho.id_restaurante,
    )

    if restaurante:
        carrinho.nome_restaurante = restaurante.nome_fantasia
        carrinho.logo_restaurante = restaurante.logo_url
    else:
        carrinho.nome_restaurante = None
        carrinho.logo_restaurante = None

    # =====================================================
    # PRODUTOS E COMPLEMENTOS
    # =====================================================

    for item in carrinho.itens:

        produto = db.get(
            Produto,
            item.id_produto,
        )

        if produto:
            item.nome_produto = produto.nome
            item.imagem_url = produto.imagem_url
        else:
            item.nome_produto = None
            item.imagem_url = None

        for item_complemento in item.complementos:

            complemento = db.get(
                Complemento,
                item_complemento.id_complemento,
            )

            if complemento:
                item_complemento.nome_complemento = complemento.nome
            else:
                item_complemento.nome_complemento = None

    return carrinho

# =========================================================
# BUSCAR CARRINHO COMPLETO
# =========================================================

def buscar_carrinho_por_id(
    db: Session,
    id_carrinho: int,
) -> Carrinho:

    stmt = (
        select(Carrinho)
        .where(
            Carrinho.id_carrinho == id_carrinho
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
            detail="Carrinho não encontrado.",
        )

    return carrinho


# =========================================================
# CRIAR CARRINHO
# =========================================================

def criar_carrinho(
    db: Session,
    id_usuario: int,
    id_restaurante: int,
) -> Carrinho:

    restaurante = db.get(
        Restaurante,
        id_restaurante,
    )

    if not restaurante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurante não encontrado.",
        )

    carrinho = Carrinho(
        id_usuario=id_usuario,
        id_restaurante=id_restaurante,
        status="ATIVO",
    )

    db.add(carrinho)
    db.flush()

    return carrinho


# =========================================================
# VALIDAR PRODUTO
# =========================================================

def validar_produto(
    db: Session,
    id_produto: int,
    id_restaurante: int,
) -> Produto:

    produto = db.get(
        Produto,
        id_produto,
    )

    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    if produto.id_restaurante != id_restaurante:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "O produto não pertence ao "
                "restaurante informado."
            ),
        )

    if not produto.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Produto inativo.",
        )

    if not produto.disponivel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Produto indisponível.",
        )

    if (
        produto.estoque is not None
        and produto.estoque <= 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Produto sem estoque.",
        )

    return produto


# =========================================================
# VALIDAR COMPLEMENTOS
# =========================================================

def validar_complementos(
    db: Session,
    id_produto: int,
    complementos_recebidos,
) -> list[tuple[Complemento, int]]:

    complementos_validados = []

    ids_recebidos = [
        item.id_complemento
        for item in complementos_recebidos
    ]

    # Evita enviar o mesmo complemento duas vezes
    if len(ids_recebidos) != len(set(ids_recebidos)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Existem complementos duplicados.",
        )

    for complemento_recebido in complementos_recebidos:

        complemento = db.get(
            Complemento,
            complemento_recebido.id_complemento,
        )

        if not complemento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Complemento "
                    f"{complemento_recebido.id_complemento} "
                    "não encontrado."
                ),
            )

        # Verifica se o grupo do complemento
        # está associado ao produto
        stmt = select(ProdutoGrupoComplemento).where(
            ProdutoGrupoComplemento.id_produto == id_produto,
            ProdutoGrupoComplemento.id_grupo
            == complemento.id_grupo,
        )

        associacao = db.scalar(stmt)

        if not associacao:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f'O complemento "{complemento.nome}" '
                    "não pertence a este produto."
                ),
            )

        if not complemento.ativo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f'O complemento "{complemento.nome}" '
                    "está inativo."
                ),
            )

        if not complemento.disponivel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f'O complemento "{complemento.nome}" '
                    "está indisponível."
                ),
            )

        if (
            complemento.estoque is not None
            and complemento.estoque
            < complemento_recebido.quantidade
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f'Estoque insuficiente para '
                    f'"{complemento.nome}".'
                ),
            )

        complementos_validados.append(
            (
                complemento,
                complemento_recebido.quantidade,
            )
        )

    return complementos_validados


# =========================================================
# ADICIONAR ITEM
# =========================================================

def adicionar_item(
    db: Session,
    id_usuario: int,
    dados: CarrinhoAdicionarItem,
) -> Carrinho:

    # -----------------------------------------
    # 1. Valida produto
    # -----------------------------------------

    produto = validar_produto(
        db=db,
        id_produto=dados.id_produto,
        id_restaurante=dados.id_restaurante,
    )

    # -----------------------------------------
    # 2. Valida estoque pela quantidade
    # -----------------------------------------

    if (
        produto.estoque is not None
        and produto.estoque < dados.quantidade
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantidade maior que o estoque disponível.",
        )

    # -----------------------------------------
    # 3. Busca carrinho ativo
    # -----------------------------------------

    carrinho = buscar_carrinho_ativo(
        db=db,
        id_usuario=id_usuario,
    )

    # -----------------------------------------
    # 4. Verifica restaurante diferente
    # -----------------------------------------

    if (
        carrinho
        and carrinho.id_restaurante
        != dados.id_restaurante
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "codigo": "CARRINHO_OUTRO_RESTAURANTE",
                "mensagem": (
                    "Você já possui itens de outro "
                    "restaurante no carrinho."
                ),
                "id_carrinho": carrinho.id_carrinho,
                "id_restaurante_atual": (
                    carrinho.id_restaurante
                ),
                "id_novo_restaurante": (
                    dados.id_restaurante
                ),
            },
        )

    # -----------------------------------------
    # 5. Valida complementos
    # -----------------------------------------

    complementos = validar_complementos(
    db=db,
    id_produto=produto.id_produto,
    complementos_recebidos=dados.complementos,
)

    # -----------------------------------------
    # 6. Cria carrinho caso não exista
    # -----------------------------------------

    if not carrinho:
        carrinho = criar_carrinho(
            db=db,
            id_usuario=id_usuario,
            id_restaurante=dados.id_restaurante,
        )

    # -----------------------------------------
    # 7. Cria item
    # -----------------------------------------

    item = CarrinhoItem(
        id_carrinho=carrinho.id_carrinho,
        id_produto=produto.id_produto,
        quantidade=dados.quantidade,
        preco_unitario=produto.preco_base,
        observacao=dados.observacao,
    )

    db.add(item)
    db.flush()

    # -----------------------------------------
    # 8. Salva complementos
    # -----------------------------------------

    for complemento, quantidade in complementos:

        item_complemento = CarrinhoItemComplemento(
            id_item=item.id_item,
            id_complemento=complemento.id_complemento,
            quantidade=quantidade,
            preco_unitario=complemento.preco_adicional,
        )

        db.add(item_complemento)

    # -----------------------------------------
    # 9. Salva transação
    # -----------------------------------------

    db.commit()

    # -----------------------------------------
    # 10. Retorna carrinho atualizado
    # -----------------------------------------

    return buscar_carrinho_por_id(
        db=db,
        id_carrinho=carrinho.id_carrinho,
    )

# =========================================================
# SUBSTITUIR CARRINHO
# =========================================================

def substituir_carrinho(
    db: Session,
    id_usuario: int,
    dados: CarrinhoAdicionarItem,
) -> Carrinho:

    carrinho_atual = buscar_carrinho_ativo(
        db=db,
        id_usuario=id_usuario,
    )

    if carrinho_atual:
        carrinho_atual.status = "CANCELADO"

        # Necessário por causa do índice único:
        # apenas um carrinho ATIVO por usuário.
        db.flush()

    try:
        return adicionar_item(
            db=db,
            id_usuario=id_usuario,
            dados=dados,
        )

    except Exception:
        db.rollback()
        raise

# =========================================================
# OBTER CARRINHO DO USUÁRIO
# =========================================================

def obter_carrinho(
    db: Session,
    id_usuario: int,
) -> Carrinho:

    carrinho = buscar_carrinho_ativo(
        db=db,
        id_usuario=id_usuario,
    )

    if not carrinho:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="O usuário não possui carrinho ativo.",
        )

    return carrinho

    # =========================================================
# ALTERAR QUANTIDADE DO ITEM
# =========================================================

def alterar_quantidade_item(
    db: Session,
    id_usuario: int,
    id_item: int,
    quantidade: int,
) -> Carrinho:

    # Busca o carrinho ativo do usuário
    carrinho = buscar_carrinho_ativo(
        db=db,
        id_usuario=id_usuario,
    )

    if not carrinho:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="O usuário não possui carrinho ativo.",
        )

    # Busca o item dentro do carrinho do usuário
    item = db.scalar(
        select(CarrinhoItem).where(
            CarrinhoItem.id_item == id_item,
            CarrinhoItem.id_carrinho == carrinho.id_carrinho,
        )
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item não encontrado no carrinho.",
        )

    # Quantidade deve ser positiva
    if quantidade < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A quantidade deve ser maior que zero.",
        )

    # Busca o produto para validar disponibilidade e estoque
    produto = db.get(
        Produto,
        item.id_produto,
    )

    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    if not produto.ativo or not produto.disponivel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Produto indisponível.",
        )

    if produto.estoque is not None and quantidade > produto.estoque:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantidade solicitada maior que o estoque disponível.",
        )

    # Atualiza quantidade
    item.quantidade = quantidade

    db.commit()

    # Retorna novamente o carrinho já carregado
    return buscar_carrinho_ativo(
        db=db,
        id_usuario=id_usuario,
    )

    # =========================================================
# REMOVER ITEM DO CARRINHO
# =========================================================

def remover_item(
    db: Session,
    id_usuario: int,
    id_item: int,
) -> Carrinho | None:

    carrinho = buscar_carrinho_ativo(
        db=db,
        id_usuario=id_usuario,
    )

    if not carrinho:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="O usuário não possui carrinho ativo.",
        )

    item = db.scalar(
        select(CarrinhoItem).where(
            CarrinhoItem.id_item == id_item,
            CarrinhoItem.id_carrinho == carrinho.id_carrinho,
        )
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item não encontrado no carrinho.",
        )

    db.delete(item)
    db.flush()

    # Verifica se ainda existe algum item no carrinho
    outro_item = db.scalar(
        select(CarrinhoItem.id_item)
        .where(
            CarrinhoItem.id_carrinho == carrinho.id_carrinho
        )
        .limit(1)
    )

    # Se removeu o último item, encerra o carrinho
    if outro_item is None:
        carrinho.status = "CANCELADO"
        db.commit()
        return None

    db.commit()

    return buscar_carrinho_ativo(
        db=db,
        id_usuario=id_usuario,
    )


# =========================================================
# ESVAZIAR CARRINHO
# =========================================================

def esvaziar_carrinho(
    db: Session,
    id_usuario: int,
) -> None:

    carrinho = buscar_carrinho_ativo(
        db=db,
        id_usuario=id_usuario,
    )

    if not carrinho:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="O usuário não possui carrinho ativo.",
        )

    for item in carrinho.itens:
        db.delete(item)

    carrinho.status = "CANCELADO"

    db.commit()
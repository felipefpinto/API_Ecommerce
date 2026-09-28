"""create endereco table

Revision ID: 2b3c4d5e6f7a
Revises: 1aee280a2f5b
Create Date: 2026-08-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2b3c4d5e6f7a"
down_revision: Union[str, Sequence[str], None] = "1aee280a2f5b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "endereco",
        sa.Column("id_endereco", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_usuario", sa.Integer(), nullable=False),
        sa.Column("apelido", sa.String(length=32), nullable=True),
        sa.Column("cep", sa.String(length=8), nullable=False),
        sa.Column("logradouro", sa.String(length=50), nullable=False),
        sa.Column("numero", sa.String(length=20), nullable=False),
        sa.Column("complemento", sa.String(length=50), nullable=True),
        sa.Column("bairro", sa.String(length=50), nullable=False),
        sa.Column("cidade", sa.String(length=50), nullable=False),
        sa.Column("uf", sa.String(length=2), nullable=False),
        sa.Column("ponto_referencia", sa.String(length=70), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["id_usuario"], ["usuario.id_usuario"]),
        sa.PrimaryKeyConstraint("id_endereco"),
        sa.CheckConstraint("cep ~ '^[0-9]{8}$'", name="ck_endereco_cep_oito_digitos"),
        sa.CheckConstraint("uf ~ '^[A-Z]{2}$'", name="ck_endereco_uf_duas_letras"),
    )
    op.create_index("ix_endereco_id_usuario", "endereco", ["id_usuario"])
    op.create_index("ix_endereco_cep", "endereco", ["cep"])


def downgrade() -> None:
    op.drop_index("ix_endereco_cep", table_name="endereco")
    op.drop_index("ix_endereco_id_usuario", table_name="endereco")
    op.drop_table("endereco")

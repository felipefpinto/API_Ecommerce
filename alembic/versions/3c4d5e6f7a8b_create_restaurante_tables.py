"""create restaurante tables

Revision ID: 3c4d5e6f7a8b
Revises: 2b3c4d5e6f7a
Create Date: 2026-09-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3c4d5e6f7a8b"
down_revision: Union[str, Sequence[str], None] = "2b3c4d5e6f7a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "responsavel_restaurante",
        sa.Column(
            "id_responsavel",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "nome",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "celular",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "ativo",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id_responsavel"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("celular"),
    )

    op.create_index(
        "ix_responsavel_restaurante_email",
        "responsavel_restaurante",
        ["email"],
    )

    op.create_index(
        "ix_responsavel_restaurante_celular",
        "responsavel_restaurante",
        ["celular"],
    )
    
    op.create_table(
        "restaurante",
        sa.Column(
            "id_restaurante",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "cnpj",
            sa.String(length=14),
            nullable=False,
        ),
        sa.Column(
            "razao_social",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "nome_fantasia",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "categoria",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "descricao",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="PENDENTE",
            nullable=False,
        ),
        sa.Column(
            "responsavel_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["responsavel_id"],
            ["responsavel_restaurante.id_responsavel"],
        ),
        sa.PrimaryKeyConstraint("id_restaurante"),
        sa.UniqueConstraint("cnpj"),
        sa.CheckConstraint(
            "cnpj ~ '^[0-9]{14}$'",
            name="ck_restaurante_cnpj_quatorze_digitos",
        ),
        sa.CheckConstraint(
            "status IN ('PENDENTE', 'DISPONIVEL', 'INATIVO')",
            name="ck_restaurante_status_valido",
        ),
    )

    op.create_index(
        "ix_restaurante_cnpj",
        "restaurante",
        ["cnpj"],
    )

    op.create_index(
        "ix_restaurante_responsavel_id",
        "restaurante",
        ["responsavel_id"],
    )

    op.create_table(
        "canal_venda",
        sa.Column("id_canal_venda", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_restaurante", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_restaurante"],
            ["restaurante.id_restaurante"],
        ),
        sa.PrimaryKeyConstraint("id_canal_venda"),
        sa.UniqueConstraint(
            "id_restaurante",
            "tipo",
            name="uq_canal_venda_restaurante_tipo",
        ),
        sa.CheckConstraint(
            "tipo IN ('ENTREGA', 'RETIRADA')",
            name="ck_canal_venda_tipo_valido",
        ),
    )
    op.create_index(
        "ix_canal_venda_id_restaurante",
        "canal_venda",
        ["id_restaurante"],
    )

    op.create_table(
        "horario_funcionamento",
        sa.Column(
            "id_horario_funcionamento",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("id_restaurante", sa.Integer(), nullable=False),
        sa.Column("dia_semana", sa.String(length=10), nullable=False),
        sa.Column("hora_abertura", sa.Time(), nullable=False),
        sa.Column("hora_fechamento", sa.Time(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_restaurante"],
            ["restaurante.id_restaurante"],
        ),
        sa.PrimaryKeyConstraint("id_horario_funcionamento"),
        sa.CheckConstraint(
            (
                "dia_semana IN ("
                "'SEGUNDA', 'TERCA', 'QUARTA', 'QUINTA', "
                "'SEXTA', 'SABADO', 'DOMINGO'"
                ")"
            ),
            name="ck_horario_funcionamento_dia_semana_valido",
        ),
        sa.CheckConstraint(
            "hora_abertura < hora_fechamento",
            name="ck_horario_funcionamento_intervalo_valido",
        ),
    )
    op.create_index(
        "ix_horario_funcionamento_id_restaurante",
        "horario_funcionamento",
        ["id_restaurante"],
    )


def downgrade() -> None:

    op.drop_index(
        "ix_horario_funcionamento_id_restaurante",
        table_name="horario_funcionamento",
    )
    op.drop_table("horario_funcionamento")

    op.drop_index(
        "ix_canal_venda_id_restaurante",
        table_name="canal_venda",
    )
    op.drop_table("canal_venda")

    op.drop_index(
        "ix_restaurante_responsavel_id",
        table_name="restaurante",
    )
    op.drop_index(
        "ix_restaurante_cnpj",
        table_name="restaurante",
    )
    op.drop_table("restaurante")

    op.drop_index(
        "ix_responsavel_restaurante_celular",
        table_name="responsavel_restaurante",
    )
    op.drop_index(
        "ix_responsavel_restaurante_email",
        table_name="responsavel_restaurante",
    )
    op.drop_table("responsavel_restaurante")
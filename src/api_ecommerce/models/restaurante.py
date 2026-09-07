from __future__ import annotations
from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_ecommerce.database.base import Base

if TYPE_CHECKING:
    from api_ecommerce.models.usuario import Usuario


class Restaurante(Base):
    __tablename__ = "restaurante"

    id_restaurante: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    cnpj: Mapped[str] = mapped_column(
        String(14),
        nullable=False,
        unique=True,
        index=True,
    )

    razao_social: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    nome_fantasia: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    categoria: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    descricao: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDENTE",
    )

    responsavel_usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuario.id_usuario"),
        nullable=False,
        index=True,
    )

    responsavel: Mapped["Usuario"] = relationship(
        back_populates="restaurantes",
    )
    canais_venda: Mapped[list["CanalVenda"]] = relationship(
        back_populates="restaurante",
        cascade="all, delete-orphan",
    )
    horarios_funcionamento: Mapped[list["HorarioFuncionamento"]] = relationship(
        back_populates="restaurante",
        cascade="all, delete-orphan",
    )


class CanalVenda(Base):
    __tablename__ = "canal_venda"

    id_canal_venda: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    id_restaurante: Mapped[int] = mapped_column(
        ForeignKey("restaurante.id_restaurante"),
        nullable=False,
        index=True,
    )

    tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    restaurante: Mapped["Restaurante"] = relationship(
        back_populates="canais_venda",
    )


class HorarioFuncionamento(Base):
    __tablename__ = "horario_funcionamento"

    id_horario_funcionamento: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    id_restaurante: Mapped[int] = mapped_column(
        ForeignKey("restaurante.id_restaurante"),
        nullable=False,
        index=True,
    )

    dia_semana: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    hora_abertura: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    hora_fechamento: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    restaurante: Mapped["Restaurante"] = relationship(
        back_populates="horarios_funcionamento",
    )

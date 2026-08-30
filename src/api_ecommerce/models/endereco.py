from __future__ import annotations
from typing import TYPE_CHECKING 
from decimal import Decimal
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_ecommerce.database.base import Base

if TYPE_CHECKING:
    from api_ecommerce.models.usuario import Usuario

# Model de endereço para usuários // Para restaurantes será implementado posteriormente;

class Endereco(Base):
    __tablename__ = "endereco"

    id_endereco: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id_usuario"),
        nullable=False,
        index=True,
    )

    apelido: Mapped[str | None] = mapped_column(String(32), nullable=True)
    cep: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    logradouro: Mapped[str] = mapped_column(String(50), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    complemento: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bairro: Mapped[str] = mapped_column(String(50), nullable=False) 
    cidade: Mapped[str] = mapped_column(String(50), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    ponto_referencia: Mapped[str | None] = mapped_column(String(70), nullable=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10,8), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(11,8), nullable=True)
    ativo: Mapped[bool] = mapped_column(default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False,default=datetime.utcnow,)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False,default=datetime.utcnow,onupdate=datetime.utcnow,)    
        

    usuario: Mapped["Usuario"] = relationship(back_populates="enderecos")

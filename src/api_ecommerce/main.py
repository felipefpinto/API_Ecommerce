from fastapi import FastAPI
from sqlalchemy import text

from api_ecommerce.database.connection import engine
from api_ecommerce.routers import endereco_router, restaurante_router, usuario_router, responsavel_restaurante_router,categoria_router
from api_ecommerce.routers.endereco_restaurante_router import router as endereco_restaurante_router
from api_ecommerce.routers.cardapio_router import router as cardapio_router
from api_ecommerce.routers.secao_cardapio_router import router as secao_cardapio_router
from api_ecommerce.routers.produto_router import router as produto_router
from api_ecommerce.routers.secao_produto_router import router as secao_produto_router
from api_ecommerce.routers.grupo_complemento_router import router as grupo_complemento_router
from api_ecommerce.routers.complemento_router import router as complemento_router
from api_ecommerce.routers import produto_sugestao_router
from api_ecommerce.routers import (
    complemento_restaurante_router,
)
from api_ecommerce.routers.configuracao_entrega_router import (
    router as configuracao_entrega_router,
)
from api_ecommerce.routers.carrinho_router import router as carrinho_router
from api_ecommerce.routers.verificacao_router import (
    router as verificacao_router,
)
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="API Ecommerce",
    description="API para plataforma de ecommerce baseada no modelo do iFood",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def root():
    return {
        "message": "API Ecommerce funcionando!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.get("/health/database")
def database_health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "database": "connected"
    }

app.include_router(usuario_router.router)
app.include_router(endereco_router.router)
app.include_router(restaurante_router.router)
app.include_router(responsavel_restaurante_router.router)
app.include_router(categoria_router.router)
app.include_router(endereco_restaurante_router)
app.mount("/uploads",StaticFiles(directory="uploads"),name="uploads",)
app.include_router(cardapio_router)
app.include_router(secao_cardapio_router)
app.include_router(produto_router)
app.include_router(secao_produto_router)
app.include_router(grupo_complemento_router)
app.include_router(complemento_router)
app.include_router(
    complemento_restaurante_router.router
)
app.include_router(
    produto_sugestao_router.router
)
app.include_router(configuracao_entrega_router)
app.include_router(carrinho_router)
app.include_router(verificacao_router)
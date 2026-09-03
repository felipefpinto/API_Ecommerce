from fastapi import FastAPI
from sqlalchemy import text

from api_ecommerce.database.connection import engine
from api_ecommerce.routers import endereco_router, usuario_router
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

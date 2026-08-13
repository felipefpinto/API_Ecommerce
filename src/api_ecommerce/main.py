from fastapi import FastAPI
from sqlalchemy import text

from api_ecommerce.database.connection import engine
from api_ecommerce.routers import usuario_router


app = FastAPI(
    title="API Ecommerce",
    description="API para plataforma de ecommerce baseada no modelo do iFood",
    version="1.0.0",
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
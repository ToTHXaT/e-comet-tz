import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.api import api as api_router

import asyncpg

from dotenv import load_dotenv

load_dotenv()


host = os.environ.get("DB_HOST")
port = os.environ.get("DB_PORT")
user = os.environ.get("DB_USER")
password = os.environ.get("DB_PASSWORD")
dbname = os.environ.get("DB_NAME")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> None:
    pool = await asyncpg.create_pool(
        host=host, port=port, user=user, password=password, database=dbname
    )
    _app.state.pool = pool
    yield
    pool.close()


app = FastAPI(lifespan=lifespan)


app.include_router(api_router, prefix="/api")

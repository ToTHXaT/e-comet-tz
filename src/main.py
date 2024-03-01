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


print(host, port, user, password, dbname)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> None:
    pool = await asyncpg.create_pool(
        host=host, port=port, user=user, password=password, database=dbname
    )

    # Checking that db has tables we need
    try:
        async with pool.acquire() as conn:
            await conn.fetch('SELECT * FROM public."Repositories" limit 1')
            await conn.fetch('SELECT * FROM public."CommitActivities" limit 1')
    except asyncpg.exceptions.UndefinedTableError:
        raise Exception("Invalid db: no valid tables Repositories and CommitActivities")

    _app.state.pool = pool
    yield
    pool.close()


app = FastAPI(lifespan=lifespan)


app.include_router(api_router, prefix="/api")

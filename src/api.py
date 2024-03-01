from datetime import date

from fastapi.routing import APIRouter
from fastapi import Request, Depends, HTTPException

from asyncpg import Pool, Connection

from src.managers import get_top100, get_activity, RepositoryInfo, CommitActivityInfo

api = APIRouter()


async def set_connection(req: Request):
    pool: Pool = req.app.state.pool
    async with pool.acquire() as conn:
        yield conn


@api.get("repos/top100", response_model=list[RepositoryInfo])
async def top100(conn: Connection = Depends(set_connection)):
    return await get_top100(conn)


@api.get("repos/{owner}/{repo}/activity", response_model=list[CommitActivityInfo])
async def activity(
    owner: str,
    repo: str,
    since: date,
    until: date,
    conn: Connection = Depends(set_connection),
):
    return await get_activity(conn, f"{owner}/{repo}", since, until)

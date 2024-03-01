from datetime import date
from typing import Literal, TypeAlias

import asyncpg
from asyncpg import Pool, Connection
from fastapi import Request, Depends, HTTPException
from fastapi.routing import APIRouter

from src.managers import get_top100, get_activity, RepositoryInfo, CommitActivityInfo


api = APIRouter()


async def set_connection(req: Request):
    pool: Pool = req.app.state.pool
    try:
        async with pool.acquire() as conn:
            yield conn
    except asyncpg.ConnectionFailureError:
        raise HTTPException(500, "Could not connect to db")


SortingField: TypeAlias = Literal[
    "repo",
    "owner",
    "position_cur",
    "position_prev",
    "stars",
    "watchers",
    "forks",
    "open_issues",
    "language",
]
SortingOrder: TypeAlias = Literal["asc", "desc"]


@api.get("repos/top100", response_model=list[RepositoryInfo])
async def top100(
    conn: Connection = Depends(set_connection),
    sorting_field: SortingField = "stars",
    sorting_order: SortingOrder = "desc",
):
    return await get_top100(conn, sorting_field, sorting_order)


@api.get("repos/{owner}/{repo}/activity", response_model=list[CommitActivityInfo])
async def activity(
    owner: str,
    repo: str,
    since: date,
    until: date,
    conn: Connection = Depends(set_connection),
):
    return await get_activity(conn, f"{owner}/{repo}", since, until)

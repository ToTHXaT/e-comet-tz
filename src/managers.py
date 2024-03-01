from datetime import date

from fastapi import HTTPException
from asyncpg import Connection

from src.schemas import RepositoryInfo, CommitActivityInfo


async def get_top100(conn: Connection, sorting_field, sorting_order) -> list[RepositoryInfo]:
    print(sorting_field)
    repos = await conn.fetch(
        f"""SELECT repo, owner, position_cur, position_prev, stars, watchers, forks, open_issues, language 
        FROM public."Repositories" ORDER BY {sorting_field} {sorting_order} LIMIT 100"""
    )

    return [
        RepositoryInfo(
            repo=res["repo"],
            owner=res["owner"],
            position_cur=res["position_cur"],
            position_prev=res["position_prev"],
            stars=res["stars"],
            watchers=res["watchers"],
            forks=res["forks"],
            open_issues=res["open_issues"],
            language=res["language"],
        )
        for res in repos
    ]


async def get_activity(
    conn: Connection, repo: str, since: date, until: date
) -> list[CommitActivityInfo]:
    if since > until:
        raise HTTPException(400, "starting date cannot be more than end date")

    commit_activities = await conn.fetch(
        """
        SELECT date, commits, authors 
        FROM public."CommitActivities" 
        WHERE repo=$1 AND date BETWEEN $2 AND $3
        ORDER BY date DESC
    """,
        repo,
        since,
        until,
    )

    return [
        CommitActivityInfo(
            date=commit_activity["date"],
            commits=commit_activity["commits"],
            authors=commit_activity["authors"],
        )
        for commit_activity in commit_activities
    ]

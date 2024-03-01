from json import JSONDecodeError
from typing import NamedTuple, TypeAlias

import datetime
from datetime import date
from datetime import datetime, timedelta

import requests
import psycopg2


token = "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"

CommitActivity: TypeAlias = dict[date, dict[str, set | int]]


class RepositoryInfo(NamedTuple):
    repo: str
    owner: str
    position_cur: int
    stars: int
    watchers: int
    forks: int
    open_issues: int
    language: str
    activity: CommitActivity


def get_popular_repositories() -> list[RepositoryInfo]:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }
    resp = requests.get(
        "https://api.github.com/search/repositories?q=stars:%3E1&sort=stars&per_page=100",
        headers=headers,
    )
    if resp.status_code != 200:
        raise Exception("Status code is not 200")

    try:
        data = resp.json()
    except JSONDecodeError as e:
        raise Exception("Invalid JSON response") from e

    if len(data["items"]) != 100:
        raise Exception("Number of repositories is not 100")

    data = data["items"]

    result = [
        RepositoryInfo(
            repo=repo["full_name"],
            owner=repo["owner"]["login"],
            position_cur=i + 1,
            stars=repo["stargazers_count"],
            watchers=repo["watchers_count"],
            forks=repo["forks_count"],
            open_issues=repo["open_issues_count"],
            language=repo["language"] or "",
            activity=get_activity_for_repo(repo["name"], repo["owner"]["login"]),
        )
        for i, repo in enumerate(data)
    ]

    return result


def get_activity_for_repo(repo: str, owner: str) -> dict[date, dict[str, set | int]]:
    commits_by_day = []

    page = 0
    while True:
        page += 1
        after = date.today() - timedelta(days=7)
        query = {"since": str(after), "per_page": 100, "page": page}
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
        }

        resp = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/commits",
            headers=headers,
            params=query,
        )

        if resp.status_code != 200:
            raise Exception(
                f"Status code is {resp.status_code=} when fetching activity for {owner=} {repo=}, {page=}"
            )
        try:
            data = resp.json()
        except JSONDecodeError as e:
            raise Exception(f"Invalid JSON response when fetching activity  for {owner=} {repo=}") from e

        commits_by_day.extend(
            (
                datetime.strptime(
                    i["commit"]["author"]["date"].split("T")[0], "%Y-%m-%d"
                ).date(),
                (
                    (i.get("author") or {}).get("login") or
                    (i.get("committer") or {}).get("login") or
                    (i["commit"].get("committer") or {}).get("name") or
                    (i["commit"].get("author") or {}).get("name")
                ),
            )
            for i in data
        )

        if len(data) < 100:
            break

    result: dict[date, dict[str, set | int]] = {}

    for commit in commits_by_day:
        if not result.get(commit[0]):
            result[commit[0]] = {"authors": set(), "total": 0}

        result[commit[0]]["authors"].add(commit[1])
        result[commit[0]]["total"] += 1

    return result


def send_data_to_db() -> None:
    with psycopg2.connect(
        host="localhost",
        dbname="cloud-e-comet-tz",
        user="dev",
        password="dev",
        port=5432,
    ) as conn:
        with conn.cursor() as curs:
            repos = get_popular_repositories()
            curs.executemany(
                """
                INSERT INTO public."Repositories"
                    (repo, owner, position_cur, position_prev, stars, watchers, forks, open_issues, language)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT(repo) DO UPDATE
                SET
                    owner = EXCLUDED.owner,
                    position_prev = (select position_cur from public."Repositories" where repo = EXCLUDED.repo),
                    position_cur = EXCLUDED.position_cur,
                    stars = EXCLUDED.stars,
                    watchers = EXCLUDED.watchers,
                    forks = EXCLUDED.forks,
                    open_issues = EXCLUDED.open_issues,
                    language = EXCLUDED.language
                """,
                [
                    (
                        repo.repo,
                        repo.owner,
                        repo.position_cur,
                        repo.position_cur,
                        repo.stars,
                        repo.watchers,
                        repo.forks,
                        repo.open_issues,
                        repo.language,
                    )
                    for repo in repos
                ],
            )
            conn.commit()

            curs.executemany(
                """
                INSERT INTO public."CommitActivities" (repo, date, commits, authors) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT(repo, date) DO NOTHING 
            """,
                [
                    (repo.repo, _date, act["total"], list(act["authors"]))
                    for repo in repos
                    for _date, act in repo.activity.items()
                ],
            )
            conn.commit()


send_data_to_db()

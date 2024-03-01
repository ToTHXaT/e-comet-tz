from datetime import date

from pydantic import BaseModel


class RepositoryInfo(BaseModel):
    repo: str
    owner: str
    position_cur: int
    position_prev: int
    stars: int
    watchers: int
    forks: int
    open_issues: int
    language: str


class CommitActivityInfo(BaseModel):
    date: date
    commits: int
    authors: list[str]

CREATE TABLE IF NOT EXISTS public."Repositories"
(
    repo character varying(128) NOT NULL,
    owner character varying(128) NOT NULL,
    position_cur integer NOT NULL,
    position_prev integer NOT NULL,
    stars integer NOT NULL,
    watchers integer NOT NULL,
    forks integer NOT NULL,
    open_issues integer NOT NULL,
    language character varying(128) NOT NULL,
    PRIMARY KEY (repo)
    );

ALTER TABLE IF EXISTS public."Repositories"
    OWNER to dev;


CREATE TABLE IF NOT EXISTS public."CommitActivities"
(
    date date NOT NULL,
    repo character varying(128) NOT NULL,
    commits integer NOT NULL,
    authors character varying[] NOT NULL,
    PRIMARY KEY (repo, date),
    CONSTRAINT commit_activities_repository_fk FOREIGN KEY (repo)
        REFERENCES public."Repositories" (repo) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

ALTER TABLE IF EXISTS public."CommitActivities"
    OWNER to dev;
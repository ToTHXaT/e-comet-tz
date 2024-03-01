FROM python:3.11

WORKDIR /code

COPY pyproject.toml poetry.lock ./
RUN pip install poetry --no-cache-dir && poetry config virtualenvs.create false && poetry install --without dev

COPY ./src/* /code/src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
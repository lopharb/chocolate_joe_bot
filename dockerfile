FROM python:3.13

WORKDIR /app

COPY . /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv sync --locked --no-dev

RUN ls

RUN . .venv/bin/activate

CMD [".venv/bin/python", "main.py"]

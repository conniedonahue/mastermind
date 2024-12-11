FROM python:3.12-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIPENV_VENV_IN_PROJECT=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --deploy --system

COPY . .

# Development stage
FROM base as development
ENV FLASK_ENV=development
CMD ["flask", "run", "--host=0.0.0.0"]

# Production stage
FROM base as production
ENV FLASK_ENV=production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "run:app"]
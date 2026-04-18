FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv sync --system

COPY wsgi.py ./
COPY service/ ./service/

RUN useradd --uid 1000 --create-home appuser && chown -R appuser /app
USER appuser

ENV PORT=8080
EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--log-level=info", "wsgi:app"]

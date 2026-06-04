FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt


FROM python:3.10-slim AS runtime

RUN groupadd -r chatbot && useradd -r -g chatbot chatbot

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY app/ ./backend/
COPY src/ ./backend/

RUN chown -R chatbot:chatbot /app

USER chatbot

WORKDIR /app/backend

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]




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

COPY backend/ ./backend/

RUN chown -R chatbot:chatbot /app

USER chatbot

WORKDIR /app/backend

EXPOSE 8000

HEALTHCHECK CMD python -c \
"import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]



# FROM python:3.10-slim AS builder

# WORKDIR /app

# # Cài đặt system dependencies cần cho build (nếu có package cần compile)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc \
#     g++ \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements file

# # Copy requirements.txt vào backend
# COPY requirements.txt .

# # Tạo virtual environment và cài đặt dependencies
# RUN python -m venv /opt/venv
# ENV PATH="/opt/venv/bin:$PATH"

# # Cài đặt dependencies vào virtual environment
# RUN --mount=type=cache,target=/root/.cache/pip \
#     pip install -r requirements.txt


# FROM python:3.10-slim AS runtime
# RUN groupadd -r chatbot && useradd -r -g chatbot chatbot

# # Copy virtual environment từ builder stage
# COPY --from=builder /opt/venv /opt/venv
# ENV PATH="/opt/venv/bin:$PATH"

# WORKDIR /app

# # Copy application code
# COPY backend/ ./backend/

# # Chuyển sang working directory là backend
# WORKDIR /app/backend

# # Chown files cho user chatbot
# RUN chown -R chatbot:chatbot /app

# # Switch sang user non-root
# USER chatbot

# # Expose port
# EXPOSE 8000

# # Health check
# HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
#   CMD curl -f http://localhost:8000/health || exit 1

# # Run FastAPI with uvicorn
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
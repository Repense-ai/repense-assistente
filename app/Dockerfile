FROM python:3.12-slim

COPY . .

RUN pip install --upgrade pip && \
    pip install uv && \
    uv sync --frozen --no-install-project --no-dev

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "./app/home.py"]
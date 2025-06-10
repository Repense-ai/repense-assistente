FROM python:3.12-slim

WORKDIR /app

# Set the application version from the VERSION file
COPY VERSION /app/
RUN echo "APP_VERSION=$(cat /app/VERSION)" >> /etc/environment

# Copy dependency files and install dependencies first
COPY pyproject.toml uv.lock ./
RUN pip install --upgrade pip && \
    pip install uv && \
    uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application code
COPY ./app .

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "Repense.py"]

FROM python:3.11-slim
WORKDIR /app

ARG VAULTSPEED_USERNAME
ARG VAULTSPEED_PASSWORD

COPY requirements.txt ./
RUN pip install --no-cache-dir \
    --extra-index-url https://${VAULTSPEED_USERNAME}:${VAULTSPEED_PASSWORD}@app.vaultspeed.com/api/artifacts/pip/vaultspeed-sdk/simple \
    -r requirements.txt

COPY app.py ./
COPY src/ ./src/

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app
USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

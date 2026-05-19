FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt ./
RUN --mount=type=secret,id=vaultspeed_username \
    --mount=type=secret,id=vaultspeed_password \
    pip install --no-cache-dir \
    --extra-index-url https://$(cat /run/secrets/vaultspeed_username):$(cat /run/secrets/vaultspeed_password)@app.vaultspeed.com/api/artifacts/pip/vaultspeed-sdk/simple \
    -r requirements.txt

COPY app.py ./
COPY src/ src/

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app
USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1
ENV ENV_PATH=.env

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

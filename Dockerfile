FROM python:slim

RUN apt-get update && \
    apt-get install -y && \
    apt-get clean

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY .env /app/

COPY . /app/

EXPOSE 8084

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8084"]

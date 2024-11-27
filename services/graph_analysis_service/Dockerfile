FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONBUFFERED=1
ENV FLASK_APP=app.py

COPY . .

CMD ["flask", "run", "--host=0.0.0.0"]
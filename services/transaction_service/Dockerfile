FROM python:3.9-slim

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONBUFFERED=1

COPY . .


EXPOSE 5001

#CMD ["python", "app.py"]
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
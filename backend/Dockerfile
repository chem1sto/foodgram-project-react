FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get -y install libpq-dev gcc
COPY ./requirements.txt ./
RUN python3 -m pip install pip --upgrade && pip3 install -r requirements.txt --no-cache-dir
COPY . ./
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]

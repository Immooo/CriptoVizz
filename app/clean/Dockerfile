FROM python:3.8-slim-buster

WORKDIR /app/clean

RUN pip install --upgrade pip
COPY requirements.txt /clean/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /clean/requirements.txt
COPY . /app/clean
#RUN
CMD [ "python", "./main.py"]
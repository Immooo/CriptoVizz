FROM python:3.8-slim-buster

WORKDIR /app/queue

RUN pip install --upgrade pip
COPY requirements.txt /queue/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /queue/requirements.txt
COPY . /app/queue
#RUN
CMD [ "python", "./main.py"]
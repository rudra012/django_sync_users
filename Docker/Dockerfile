FROM python:3.7
ENV PYTHONUNBUFFERED 1
ENV REDIS_HOST "redis"

RUN mkdir -p /opt/services/app/src
RUN mkdir -p /opt/services/app/src/static
WORKDIR /opt/services/app/src

COPY . /opt/services/app/src

RUN pip install -r requirements.txt
RUN python manage.py migrate
RUN python manage.py collectstatic --no-input
# RUN apt-get update && apt-get install -y libproj-dev gdal-bin

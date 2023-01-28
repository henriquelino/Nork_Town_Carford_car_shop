FROM python:3.9-slim-buster

ENV DEBUG=1
ENV ALLOWED_HOSTS=127.0.0.1



ENV DJANGO_SETTINGS_MODULE=cardford.settings
ENV SECRET_KEY=mysecretkey
ENV SUPERUSER_USERNAME=admin
ENV SUPERUSER_EMAIL=admin@example.com
ENV SUPERUSER_PASSWORD=password

EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh
COPY requirements.txt /requirements.txt
COPY ./app /app


RUN apt-get update && apt-get -y install libpq-dev gcc
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


WORKDIR /app

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

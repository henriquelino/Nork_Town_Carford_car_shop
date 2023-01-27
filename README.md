**all these commands are at project root:**

create migrations with:
`python ./app/manage.py makemigrations`

apply migrations with:
`python ./app/manage.py migrate`

create superuser:
`python ./app/manage.py createsuperuser --username admin --email admin@example.com`

run with:
`python ./app/manage.py runserver`

run tests with
`coverage run --source=app --omit=*/migrations/* ./app/manage.py test`


build docker and run with
`docker-compose up --force-recreate`
add `--detach` to run on background
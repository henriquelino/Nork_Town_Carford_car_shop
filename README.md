**all these commands are meant to run @ root, adjust if needed**

# To develop:
After code changes, use `tox` to lint and run tests, if everything is ok, then you are good to go :)

# To run:
create migrations with:
`python ./app/manage.py makemigrations`

apply migrations with:
`python ./app/manage.py migrate`

create superuser:
`python ./app/manage.py createsuperuser --username admin --email admin@example.com`

run with:
`python ./app/manage.py runserver`

run tests with
`coverage run`
*tip: the extra arguments for the command comes from setup.cfg file*


build docker
`docker-compose build`

 and run with
 `docker-compose up`
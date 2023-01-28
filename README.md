
# The case:
### Description
Nork-Town is a weird place. Crows cawk the misty morning while old men squint. It’s a small
town, so the mayor had a bright idea to limit the number of cars a person may possess.

One person may have up to 3 vehicles.
The vehicle, registered to a person, may have one color, 'yellow', 'blue' or 'gray'. And one of three models, 'hatch', 'sedan' or 'convertible'.

Carford car shop want a system where they can add car owners and cars.
Car owners may not have cars yet, they need to be marked as a sale opportunity.
Cars cannot exist in the system without owners.

### Requirements
* Setup the dev environment with docker
* Using docker-compose with as many volumes as it takes
* Use Python’s Flask framework and any other library
* Use any SQL database
* Secure routes
* Write tests
  
---

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
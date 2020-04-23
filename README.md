# About
A simple wrapper/cache of the [Ghibli API](http://ghibliapi.herokuapp.com).

# Requirements

## System packages
The application uses celery for periodic tasks. Thus, it requires a message 
broker (e.g. redis, RabbitMQ etc). By default (see "gh_films.settings.demo") 
you're supposed to use the redis server as a message broker.

Beside that you need python (3.6+), "pip", "setuptools" and, probably, 
virtualenv (to build python's virtual environment)

## Python packages
To install python packages you may just say something like 
```bash
pip install -r ./requirements.txt
```
Also, please note, that there's an additional file `requirements_test.txt` 
which contains additional packages for testing. In other words, if you want to
run tests you'll need to install those packages first. 

# Usage
Before run this application you need to do next steps:
  1. create virtual environment and activate it;
  2. install required packages (system and python);
  3. create you own local settings (e.g. you may just copy 
     `gh_films/settings/demo.py` to `gh_films/settings/local.py`);
  4. run migrations (e.g. `./manage.py migrate`);
  5. run celery beat with single worker (e.g. 
     `celery -A gh_films worker -l info -B -c 1`);
  6. wait until celery downloads data from Ghibli's server (about 50 secodns);
  7. in separate terminal window/tab run server (e.g. `./manage.py runserver`);
  8. in web browser go to the url: http://127.0.0.1:8000/movies/

Note, the `dh_films.settings.demo` is configured to use sqlite DB in the 
current directory (in the project's directory). Thus user that runs server 
should have permissions to write into that folder.

# Testing
Before run tests you're supposed to have installed packages from 
`requirements_test.txt`. After that you may just say `./manage.py test`.

## Tox
If you want to test the package in several environments at once you may use 
the `tox.ini`. Please note, in this case you need to install the `tox` package
manually via `pip install tox`.


# Known issues
The current version ("0.0.1") supports tracking and adding new items 
("films", "people" and relations between them) only. It can't detect updating 
of any item's fields if the `id` property is the same.   

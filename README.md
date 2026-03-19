# Eol api

![https://github.com/eol-uchile/eol-api/actions](https://github.com/eol-uchile/eol-api/workflows/Python%20application/badge.svg)

Allows to send student and grades info from an url

# Install App

    docker-compose exec lms pip install -e /openedx/requirements/eol_api
    
    docker-compose exec lms python manage.py lms --settings=prod.production makemigrations eol_api


## TESTS
**Prepare tests:**

- Install **act** following the instructions in [https://nektosact.com/installation/index.html](https://nektosact.com/installation/index.html)

**Run tests:**
- In a terminal at the root of the project
    ```
    act -W .github/workflows/pythonapp.yml
    ```

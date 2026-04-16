# Eol api

![Coverage Status](/coverage-badge.svg)

![https://github.com/eol-uchile/eol-api/actions](https://github.com/eol-uchile/eol-api/workflows/Python%20application/badge.svg)

Allows to send student and grades info from an url

# Install App

    docker-compose exec lms pip install -e /openedx/requirements/eol_api
    
    docker-compose exec lms python manage.py lms --settings=prod.production migrate eol_api


## StudentGrades API
This API allows retrieving course-related information filtered by specific criteria. It requires a course_id parameter, which must be a non-empty string identifying the course. Optionally, a from_date parameter can be provided to filter results starting from a given date; it accepts the formats DD-MM-YYYY, DD-MM-YYYY HH:MM, and DD-MM-YYYY HH:MM:SS. Additionally, the passed parameter is optional and indicates whether to return only records that meet the approval condition, defaulting to true if not specified.

`GET /api/student_grades`

You should have installed edx-rest-api-client

```python
client = OAuthAPIClient('https://lms/oauth2/access_token', 'client_id', 'client_secret')
data= {
        "course_id": "course-v1:org+code+run",
        "passed": True,
        "from_date": "2025-07-20"
    }
client.get('https://lms/api/student_grades', data)
```

### Example results
```json
[
    {
    "course_data":{
            "cutoff":0.5,
            "display_name": "Nombre del curso",
            "ucursos_id": "course/test/map",
            "id_course": "course-v1:org+code+run"
        },
        "student_data":[
            {
                "document_id":"11111111-1",
                "passed_timestamp": "2025-07-25T00:00:00Z",
                "percent_grade": 0.8,
                "grade": 5.8
            },
            {
                "document_id":"22222222-2",
                "passed_timestamp": "2025-07-15T00:00:00Z",
                "percent_grade": 0.4,
                "grade": 3.4
            }
        ]
    }
]
```

## ClientCourses API
This API allows you to obtain a list of course_ids that have access from an application and are connected through ClientCourseAccess model

`GET /api/get_client_courses`

You should have installed edx-rest-api-client

```python
client = OAuthAPIClient('https://lms/oauth2/access_token', 'client_id', 'client_secret')

client.get('https://lms/api/get_client_courses')
```

### Example result
```json
{
    "courses_ids":["course-v1:org+code+run","course-v1:org2+code2+run"]
}
```

## TESTS
**Prepare tests:**

- Install **act** following the instructions in [https://nektosact.com/installation/index.html](https://nektosact.com/installation/index.html)

**Run tests:**
- In a terminal at the root of the project
    ```
    act -W .github/workflows/pythonapp.yml
    ```

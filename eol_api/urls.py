# Installed packages (via pip)
from django.conf.urls import url

# Internal project dependencies
from .api import StudentGrades, ClientCourses

urlpatterns = [
    url(
        r'^api/student_grades/',
        StudentGrades.as_view(),
        name='student_grades'
    ),
    url(
        r'^api/get_client_courses/',
        ClientCourses.as_view(),
        name='get_client_courses',
    )
]

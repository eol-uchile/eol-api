# Installed packages (via pip)
from django.conf.urls import url

# Internal project dependencies
from .api import StudentGrades

urlpatterns = [
    url(
        r'^api/student_grades/',
        StudentGrades.as_view(),
        name='student_grades'
    )
]

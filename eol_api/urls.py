# Installed packages (via pip)
from django.conf.urls import url

# Internal project dependencies
from .api import StudentPerCourse

urlpatterns = [
    url(
        r'^api/get_student_per_course/',
        StudentPerCourse.as_view(),
        name='student_per_course'
    )
]

# Python Standard Libraries
import datetime

# Installed packages (via pip)
from django.contrib.auth.models import User
from django.db import models

# Edx dependencies
from oauth2_provider.models import Application
from opaque_keys.edx.django.models import CourseKeyField

class ClientCourseAccess(models.Model):
    client = models.ForeignKey(Application, on_delete=models.CASCADE)
    course_id = course_id = CourseKeyField(max_length=255, db_index=True, unique=True,verbose_name=('course'))
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

# Python Standard Libraries
import uuid

# Installed packages (via pip)
from django.contrib.auth.models import User
from django.db import models
from simple_history.models import HistoricalRecords

# Edx dependencies
from oauth2_provider.models import Application
from opaque_keys.edx.django.models import CourseKeyField

class ClientCourseAccess(models.Model):
    client = models.ForeignKey(Application, on_delete=models.CASCADE)
    course_id = CourseKeyField(max_length=255, db_index=True, verbose_name=('course'))
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # An audit row will be created for every change to a ClientCourseAccess. This
    # will create a new model behind the scenes - HistoricalClientCourseAccess and a
    # table named 'eol_api_clientcourseaccess_history'.
    history = HistoricalRecords(
        history_id_field=models.UUIDField(default=uuid.uuid4),
        table_name='eol_api_clientcourseaccess_history'
    )

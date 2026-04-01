# -*- coding:utf-8 -*-
# Installed packages (via pip)
from django.contrib import admin

# Internal project dependencies
from .models import ClientCourseAccess

class ClientCourseAccessAdmin(admin.ModelAdmin):
    list_display = ('client', 'course_id', 'created','created_by',)
    search_fields = ['course_id', 'created',]

admin.site.register(ClientCourseAccess, ClientCourseAccessAdmin)

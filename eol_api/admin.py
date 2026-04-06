# -*- coding:utf-8 -*-
# Installed packages (via pip)
from django.contrib import admin

# Internal project dependencies
from .models import ClientCourseAccess

class ClientCourseAccessAdmin(admin.ModelAdmin):
    list_display = ('client', 'course_id', 'created','created_by',)
    search_fields = ['course_id', 'created',]

    # save user when is created
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_exclude(self, request, obj=None):
        if obj is None:
            return ('created_by',)
        return ()

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('created_by',)
        return ()

admin.site.register(ClientCourseAccess, ClientCourseAccessAdmin)

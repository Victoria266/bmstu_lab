from django.contrib import admin

from .models import *

admin.site.register(Resource)
admin.site.register(Report)
admin.site.register(ResourceReport)

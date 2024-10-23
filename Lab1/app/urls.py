from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('resources/<int:resource_id>/', resource),
    path('reports/<int:report_id>/', report),
]
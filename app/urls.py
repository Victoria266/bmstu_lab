from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('resources/<int:resource_id>/', resource_details, name="resource_details"),
    path('resources/<int:resource_id>/add_to_report/', add_resource_to_draft_report, name="add_resource_to_draft_report"),
    path('reports/<int:report_id>/delete/', delete_report, name="delete_report"),
    path('reports/<int:report_id>/', report)
]

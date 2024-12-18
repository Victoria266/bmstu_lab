from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/resources/', search_resources),  # GET
    path('api/resources/<int:resource_id>/', get_resource_by_id),  # GET
    path('api/resources/<int:resource_id>/update/', update_resource),  # PUT
    path('api/resources/<int:resource_id>/update_image/', update_resource_image),  # POST
    path('api/resources/<int:resource_id>/delete/', delete_resource),  # DELETE
    path('api/resources/create/', create_resource),  # POST
    path('api/resources/<int:resource_id>/add_to_report/', add_resource_to_report),  # POST

    # Набор методов для заявок
    path('api/reports/', search_reports),  # GET
    path('api/reports/<int:report_id>/', get_report_by_id),  # GET
    path('api/reports/<int:report_id>/update/', update_report),  # PUT
    path('api/reports/<int:report_id>/update_status_user/', update_status_user),  # PUT
    path('api/reports/<int:report_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/reports/<int:report_id>/delete/', delete_report),  # DELETE

    # Набор методов для м-м
    path('api/reports/<int:report_id>/update_resource/<int:resource_id>/', update_resource_in_report),  # PUT
    path('api/reports/<int:report_id>/delete_resource/<int:resource_id>/', delete_resource_from_report),  # DELETE

    # Набор методов для аутентификации и авторизации
    path("api/users/register/", register),  # POST
    path("api/users/login/", login),  # POST
    path("api/users/logout/", logout),  # POST
    path("api/users/<int:user_id>/update/", update_user)  # PUT
]

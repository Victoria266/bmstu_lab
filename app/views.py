import random

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .management.commands.fill_db import calc
from .serializers import *


def get_draft_report():
    return Report.objects.filter(status=1).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


@api_view(["GET"])
def search_resources(request):
    resource_density = request.GET.get("resource_density", "")

    resources = Resource.objects.filter(status=1)

    if resource_density:
        resources = resources.filter(name__icontains=resource_density)

    serializer = ResourcesSerializer(resources, many=True)
    
    draft_report = get_draft_report()

    resp = {
        "resources": serializer.data,
        "resources_count": ResourceReport.objects.filter(report=draft_report).count() if draft_report else None,
        "draft_report": draft_report.pk if draft_report else None
    }

    return Response(resp)


@api_view(["GET"])
def get_resource_by_id(request, resource_id):
    if not Resource.objects.filter(pk=resource_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resource = Resource.objects.get(pk=resource_id)
    serializer = ResourceSerializer(resource)

    return Response(serializer.data)


@api_view(["PUT"])
def update_resource(request, resource_id):
    if not Resource.objects.filter(pk=resource_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resource = Resource.objects.get(pk=resource_id)

    serializer = ResourceSerializer(resource, data=request.data, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_resource(request):
    serializer = ResourceSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Resource.objects.create(**serializer.validated_data)

    resources = Resource.objects.filter(status=1)
    serializer = ResourceSerializer(resources, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_resource(request, resource_id):
    if not Resource.objects.filter(pk=resource_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resource = Resource.objects.get(pk=resource_id)
    resource.status = 2
    resource.save()

    resources = Resource.objects.filter(status=1)
    serializer = ResourceSerializer(resources, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_resource_to_report(request, resource_id):
    if not Resource.objects.filter(pk=resource_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resource = Resource.objects.get(pk=resource_id)

    draft_report = get_draft_report()

    if draft_report is None:
        draft_report = Report.objects.create()
        draft_report.owner = get_user()
        draft_report.date_created = timezone.now()
        draft_report.save()

    if ResourceReport.objects.filter(report=draft_report, resource=resource).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    item = ResourceReport.objects.create()
    item.report = draft_report
    item.resource = resource
    item.save()

    serializer = ReportSerializer(draft_report)
    return Response(serializer.data["resources"])


@api_view(["POST"])
def update_resource_image(request, resource_id):
    if not Resource.objects.filter(pk=resource_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resource = Resource.objects.get(pk=resource_id)

    image = request.data.get("image")
    if image is not None:
        resource.image = image
        resource.save()

    serializer = ResourceSerializer(resource)

    return Response(serializer.data)


@api_view(["GET"])
def search_reports(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    reports = Report.objects.exclude(status__in=[1, 5])

    if status > 0:
        reports = reports.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        reports = reports.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        reports = reports.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = ReportsSerializer(reports, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_report_by_id(request, report_id):
    if not Report.objects.filter(pk=report_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    report = Report.objects.get(pk=report_id)
    serializer = ReportSerializer(report, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_report(request, report_id):
    if not Report.objects.filter(pk=report_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    report = Report.objects.get(pk=report_id)
    serializer = ReportSerializer(report, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, report_id):
    if not Report.objects.filter(pk=report_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    report = Report.objects.get(pk=report_id)

    if report.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    report.status = 2
    report.date_formation = timezone.now()
    report.save()

    serializer = ReportSerializer(report, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, report_id):
    if not Report.objects.filter(pk=report_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    report = Report.objects.get(pk=report_id)

    if report.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        for item in ResourceReport.objects.filter(report=report):
            item.volume = random.randint(1, 10)
            item.save()

    report.date_complete = timezone.now()
    report.status = request_status
    report.moderator = get_moderator()
    report.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_report(request, report_id):
    if not Report.objects.filter(pk=report_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    report = Report.objects.get(pk=report_id)

    if report.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    report.status = 5
    report.save()

    serializer = ReportSerializer(report, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_resource_from_report(request, report_id, resource_id):
    if not ResourceReport.objects.filter(report_id=report_id, resource_id=resource_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ResourceReport.objects.get(report_id=report_id, resource_id=resource_id)
    item.delete()

    items = ResourceReport.objects.filter(report_id=report_id)
    data = [ResourceItemSerializer(item.resource, context={"plan_volume": item.plan_volume}).data for item in items]

    return Response(data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_resource_in_report(request, report_id, resource_id):
    if not ResourceReport.objects.filter(resource_id=resource_id, report_id=report_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ResourceReport.objects.get(resource_id=resource_id, report_id=report_id)

    serializer = ResourceReportSerializer(item, data=request.data,  partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)
import random
import uuid

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .permissions import *
from .redis import session_storage
from .serializers import *
from .utils import identity_user, get_session


def get_draft_report(request):
    user = identity_user(request)

    if user is None:
        return None

    report = Report.objects.filter(owner=user).filter(status=1).first()

    return report


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'query',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_resources(request):
    resource_density = request.GET.get("resource_density", "")

    resources = Resource.objects.filter(status=1)

    if resource_density:
        resources = resources.filter(name__icontains=resource_density)

    serializer = ResourcesSerializer(resources, many=True)

    draft_report = get_draft_report(request)

    resp = {
        "resources": serializer.data,
        "resources_count": ResourceReport.objects.filter(report=draft_report).count() if draft_report else None,
        "draft_report_id": draft_report.pk if draft_report else None
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
@permission_classes([IsModerator])
def update_resource(request, resource_id):
    if not Resource.objects.filter(pk=resource_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resource = Resource.objects.get(pk=resource_id)

    serializer = ResourceSerializer(resource, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsModerator])
def create_resource(request):
    serializer = ResourceSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Resource.objects.create(**serializer.validated_data)

    resources = Resource.objects.filter(status=1)
    serializer = ResourceSerializer(resources, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_resource(request, resource_id):
    if not Resource.objects.filter(pk=resource_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resource = Resource.objects.get(pk=resource_id)
    resource.status = 2
    resource.save()

    resource = Resource.objects.filter(status=1)
    serializer = ResourceSerializer(resource, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_resource_to_report(request, resource_id):
    if not Resource.objects.filter(pk=resource_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resource = Resource.objects.get(pk=resource_id)

    draft_report = get_draft_report(request)

    if draft_report is None:
        draft_report = Report.objects.create()
        draft_report.date_created = timezone.now()
        draft_report.owner = identity_user(request)
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
@permission_classes([IsModerator])
def update_resource_image(request, resource_id):
    if not Resource.objects.filter(pk=resource_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resource = Resource.objects.get(pk=resource_id)

    image = request.data.get("image")

    if image is None:
        return Response(status.HTTP_400_BAD_REQUEST)

    resource.image = image
    resource.save()

    serializer = ResourceSerializer(resource)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_reports(request):
    status_id = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    reports = Report.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        reports = reports.filter(owner=user)

    if status_id > 0:
        reports = reports.filter(status=status_id)

    if date_formation_start and parse_datetime(date_formation_start):
        reports = reports.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        reports = reports.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = ReportsSerializer(reports, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_report_by_id(request, report_id):
    user = identity_user(request)

    if not Report.objects.filter(pk=report_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    report = Report.objects.get(pk=report_id)
    serializer = ReportSerializer(report)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=ReportSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_report(request, report_id):
    user = identity_user(request)

    if not Report.objects.filter(pk=report_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    report = Report.objects.get(pk=report_id)
    serializer = ReportSerializer(report, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, report_id):
    user = identity_user(request)

    if not Report.objects.filter(pk=report_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    report = Report.objects.get(pk=report_id)

    if report.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    report.status = 2
    report.date_formation = timezone.now()
    report.save()

    serializer = ReportSerializer(report)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsModerator])
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

    report.status = request_status
    report.date_complete = timezone.now()
    report.moderator = identity_user(request)
    report.save()

    serializer = ReportSerializer(report)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_report(request, report_id):
    user = identity_user(request)

    if not Report.objects.filter(pk=report_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    report = Report.objects.get(pk=report_id)

    if report.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    report.status = 5
    report.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_resource_from_report(request, report_id, resource_id):
    user = identity_user(request)

    if not Report.objects.filter(pk=report_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not ResourceReport.objects.filter(report_id=report_id, resource_id=resource_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ResourceReport.objects.get(report_id=report_id, resource_id=resource_id)
    item.delete()

    report = Report.objects.get(pk=report_id)

    serializer = ReportSerializer(report)
    resources = serializer.data["resources"]

    return Response(resources)


@swagger_auto_schema(method='PUT', request_body=ResourceReportSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_resource_in_report(request, report_id, resource_id):
    user = identity_user(request)

    if not Report.objects.filter(pk=report_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not ResourceReport.objects.filter(resource_id=resource_id, report_id=report_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ResourceReport.objects.get(resource_id=resource_id, report_id=report_id)

    serializer = ResourceReportSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    user = identity_user(request)

    if serializer.is_valid():
        user = authenticate(**serializer.data)
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        session_id = str(uuid.uuid4())
        session_storage.set(session_id, user.id)

        serializer = UserSerializer(user)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        response.set_cookie("session_id", session_id, samesite="lax")

        return response

    if user is not None:
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@swagger_auto_schema(method='PUT', request_body=UserProfileSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    password = request.data.get("password", None)
    if password is not None and not user.check_password(password):
        user.set_password(password)
        user.save()

    return Response(serializer.data, status=status.HTTP_200_OK)

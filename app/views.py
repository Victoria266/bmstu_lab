from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import Resource, Report, ResourceReport


def index(request):
    resource_density = request.GET.get("resource_density", "")
    resources = Resource.objects.filter(status=1)

    if resource_density:
        resources = resources.filter(density__gt=float(resource_density))

    draft_report = get_draft_report()

    context = {
        "resource_density": resource_density,
        "resources": resources
    }

    if draft_report:
        context["resources_count"] = len(draft_report.get_resources())
        context["draft_report"] = draft_report

    return render(request, "resources_page.html", context)


def add_resource_to_draft_report(request, resource_id):
    resource = Resource.objects.get(pk=resource_id)

    draft_report = get_draft_report()

    if draft_report is None:
        draft_report = Report.objects.create()
        draft_report.owner = get_current_user()
        draft_report.date_created = timezone.now()
        draft_report.save()

    if ResourceReport.objects.filter(report=draft_report, resource=resource).exists():
        return redirect("/")

    item = ResourceReport(
        report=draft_report,
        resource=resource
    )
    item.save()

    return redirect("/")


def resource_details(request, resource_id):
    context = {
        "resource": Resource.objects.get(id=resource_id)
    }

    return render(request, "resource_page.html", context)


def delete_report(request, report_id):
    if not Report.objects.filter(pk=report_id).exists():
        return redirect("/")

    with connection.cursor() as cursor:
        cursor.execute("UPDATE reports SET status=5 WHERE id = %s", [report_id])

    return redirect("/")


def report(request, report_id):
    if not Report.objects.filter(pk=report_id).exists():
        return redirect("/")

    report = Report.objects.get(id=report_id)
    if report.status == 5:
        return redirect("/")

    context = {
        "report": report,
    }

    return render(request, "report_page.html", context)


def get_draft_report():
    return Report.objects.filter(status=1).first()


def get_current_user():
    return User.objects.filter(is_superuser=False).first()
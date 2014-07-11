from wkcdd.models import Project
from wkcdd.models import Report

from pyramid.view import view_config


@view_config(route_name='export_projects', renderer="xlsx")
def export_projects(request):
    projects = Project.all()
    return {
        'projects': projects,
        'is_project_export': True
    }


@view_config(route_name='export_reports', renderer="xlsx")
def export_reports(request):
    reports = Report.all()

    return {
        'reports': reports,
        'is_report_export': True
    }

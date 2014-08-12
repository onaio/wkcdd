from wkcdd.models import Project
from wkcdd.models.period import Period

from pyramid.view import view_config


@view_config(route_name='exports',
             renderer='exports.jinja2',
             request_method='GET')
def export(request):
    available_periods = Period.get_periods_available()
    quarters = {p.quarter for p in available_periods}
    years = {p.year for p in available_periods}
    return {
        'quarters': quarters,
        'years': years
    }


@view_config(route_name='export_projects', renderer="xlsx")
def export_projects(request):

    projects = Project.all()
    return {
        'projects': projects,
        'is_project_export': True
    }


@view_config(route_name='export_reports', renderer="xlsx")
def export_reports(request):
    quarter = request.GET.get('quarter')
    year = request.GET.get('year')

    period = None

    if quarter and year:
        period = Period(quarter=quarter, year=year)

    projects = Project.all()

    return {
        'projects': projects,
        'is_report_export': True,
        'period': period
    }

import json
from pyramid.view import (
    view_config,
    view_defaults,
)

from wkcdd.models.project import (
    ProjectType,
    Project,
    ProjectFactory
)


from wkcdd import constants

from wkcdd.libs.utils import tuple_to_dict_list
from wkcdd.views.helpers import filter_projects_by
from wkcdd.models import (
    County,
    SubCounty,
    Constituency,
    Community,
)


@view_defaults(route_name='projects')
class ProjectViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=ProjectFactory,
                 renderer='projects_list.jinja2',
                 request_method='GET')
    def list(self):
        project_types = ProjectType.all()
        search_criteria = {}
        # Filter
        filter_projects = self.request.GET.get('filter')
        if filter_projects is not None:
            search = self.request.GET.get('search') or ''
            sector = self.request.GET.get('sector') or ''
            location = (self.request.GET.get('community') or
                        self.request.GET.get('constituency') or
                        self.request.GET.get('sub_county') or
                        self.request.GET.get('county') or
                        None)
            search_criteria = {'name': search,
                               'sector': sector,
                               'location': location}

            projects = filter_projects_by(search_criteria)

        else:
            projects = Project.all()

        # get locations (count and sub-county)
        locations = Project.get_locations(projects)
        # get filter criteria
        filter_criteria = Project.get_filter_criteria()
        project_geopoints = [
            {'id': project.id,
             'name': project.name,
             'sector': project.sector_name,
             'lat': str(project.latlong[0]),
             'lng': str(project.latlong[1])}
            for project in projects
            if project.latlong]
        project_geopoints = json.dumps(project_geopoints)
        return {
            'project_types': project_types,
            'projects': projects,
            'locations': locations,
            'filter_criteria': filter_criteria,
            'project_geopoints': project_geopoints,
            'search_criteria': search_criteria
        }

    @view_config(name='show',
                 context=Project,
                 renderer='projects_show.jinja2',
                 request_method='GET')
    def show(self):
        project = self.request.context
        report = project.get_latest_report()
        # TODO filter by periods
        # periods = [report.period for report in reports]
        if report:
            performance_indicators = report.calculate_performance_indicators()
            impact_indicators = report.calculate_impact_indicators()
            return {
                'project': project,
                'performance_indicators': performance_indicators,
                'impact_indicators': impact_indicators,
                'performance_indicator_mapping': tuple_to_dict_list(
                    ('title', 'group'),
                    constants.PERFORMANCE_INDICATOR_REPORTS[
                        report.report_data[constants.XFORM_ID]]),
                'impact_indicator_mapping': tuple_to_dict_list(
                    ('title', 'key'),
                    constants.IMPACT_INDICATOR_REPORT),
            }
        else:
            return {
                'project': project,
                'performance_indicators': None,
                'performance_indicator_mapping': None,
                'impact_indicators': None,
            }

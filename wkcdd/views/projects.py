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
        # Search for projects
        search_term = self.request.GET.get('search')
        if search_term is not None:
            projects = Project.all(Project.name.ilike("%"+search_term+"%"))
        else:
            projects = Project.all()

        # Filter by filter criteria
        filter_list = self.request.GET.get('filter')
        if filter_list is not None:
            sector_id = self.request.GET.get('sector')
            county_id = self.request.GET.get('county')
            sub_county_id = self.request.GET.get('sub_county')
            constituency_id = self.request.GET.get('constituency')
            community_id = self.request.GET.get('community')


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
            'project_geopoints': project_geopoints
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

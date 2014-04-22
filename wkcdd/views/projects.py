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

        # Filter
        filter_projects = self.request.GET.get('filter')
        if filter_projects is not None:

            search_term = self.request.GET.get('search')
            if search_term:
                projects = filter_projects_by("name", search_term)

            sector_id = self.request.GET.get('sector')
            if sector_id:
                projects = filter_projects_by("sector", sector_id)

            county_id = self.request.GET.get("county")
            if county_id:
                projects = filter_projects_by(County, county_id)

            sub_county_id = self.request.GET.get('sub_county')
            if sub_county_id:
                projects = filter_projects_by(SubCounty, sub_county_id)

            constituency_id = self.request.GET.get('constituency')
            if constituency_id:
                projects = filter_projects_by(Constituency, constituency_id)

            community_id = self.request.GET.get('community')
            if community_id:
                projects = filter_projects_by(Community, community_id)

            filters = {'name': self.request.GET.get('search'),
                       'sector': self.request.GET.get('sector'),
                       County: self.request.GET.get('county'),
                       SubCounty: self.request.GET.get('sub_county'),
                       Constituency: self.request.GET.get('constituency'),
                       Community: self.request.GET.get('community')}

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

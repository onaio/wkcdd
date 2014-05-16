from collections import defaultdict
from pyramid.view import (
    view_config,
    view_defaults,
)

from wkcdd.models.project import (
    ProjectType,
    Project,
    ProjectFactory
)
from wkcdd.models import Report
from wkcdd import constants
from wkcdd.libs.utils import (
    tuple_to_dict_list,
    get_impact_indicator_list)
from wkcdd.views.helpers import (
    filter_projects_by,
    get_project_geolocations,
    build_report_period_criteria)


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
        search_criteria = defaultdict(str)
        # Filter
        filter_projects = self.request.GET.get('filter')
        if filter_projects is not None:
            search = self.request.GET.get('search', '')
            sector = self.request.GET.get('sector', '')
            location_map = {
                'community': self.request.GET.get('community'),
                'constituency': self.request.GET.get('constituency'),
                'sub_county': self.request.GET.get('sub_county'),
                'county': self.request.GET.get('county')
            }
            search_criteria = {'name': search,
                               'sector': sector,
                               'location_map': location_map}

            projects = filter_projects_by(search_criteria)

        else:
            projects = Project.all()

        # get locations (count and sub-county)
        locations = Project.get_locations(projects)
        # get filter criteria
        filter_criteria = Project.generate_filter_criteria()
        project_geopoints = get_project_geolocations(projects)
        return {
            'project_types': project_types,
            'projects': projects,
            'locations': locations,
            'filter_criteria': filter_criteria,
            'project_geopoints': project_geopoints,
            'search_criteria': search_criteria
        }

    @view_config(name='',
                 context=Project,
                 renderer='projects_show.jinja2',
                 request_method='GET')
    def show(self):
        project = self.request.context

        # define criteria

        month_or_quarter = self.request.GET.get('month_or_quarter', '')
        period = self.request.GET.get('period', '')

        # filter by period
        criteria = build_report_period_criteria(month_or_quarter, period)

        reports = Report.get_reports_for_projects([project], *criteria)

        # periods = [report.period for report in reports]
        if reports:
            # limit report to the latest report within the period
            report = reports[0]
            performance_indicators = report.calculate_performance_indicators()
            impact_indicators = report.calculate_impact_indicators()
            impact_indicator_mapping = get_impact_indicator_list(
                constants.IMPACT_INDICATOR_KEYS)
            return {
                'project': project,
                'performance_indicators': performance_indicators,
                'impact_indicators': impact_indicators,
                'performance_indicator_mapping': tuple_to_dict_list(
                    ('title', 'group'),
                    constants.PERFORMANCE_INDICATOR_REPORTS[
                        report.report_data[constants.XFORM_ID]]),
                'impact_indicator_mapping': impact_indicator_mapping
            }
        else:
            return {
                'project': project,
                'performance_indicators': None,
                'performance_indicator_mapping': None,
                'impact_indicators': None,
            }

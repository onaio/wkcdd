from pyramid.view import (
    view_config,
    view_defaults,
)

from wkcdd.models.project import (
    ProjectType,
    Project,
    ProjectFactory
)

from wkcdd.models.location import (
    Location,
    LocationType
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
        projects = Project.all()

        #get count and sub-county
        locations = {}
        for project in projects:
            constituency = project.community.constituency
            sub_county = Location.get(Location.id == constituency.parent_id,
                                      Location.location_type ==
                                      LocationType.
                                      get_or_create('sub_county').id)
            county = Location.get(Location.id == sub_county.parent_id,
                                  Location.location_type ==
                                  LocationType.get_or_create('county').id)
            locations[project.id] = [county, sub_county]

        return {
            'project_types': project_types,
            'projects': projects,
            'locations': locations
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
                    constants.IMPACT_INDICATOR_REPORT)
            }
        else:
            return {
                'project': project,
                'performance_indicators': None,
                'performance_indicator_mapping': None,
                'impact_indicators': None
            }

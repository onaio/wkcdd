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
        projects = Project.all()

        #get locations (count and sub-county)
        locations = Project.get_locations(projects)

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
        reports = project.reports
        # TODO filter by periods
        # periods = [report.period for report in reports]
        report = reports[0]
        performance_indicators = report.calculate_performance_indicators()
        #TODO ensure the 1st report belongs to the latest period
        # impact_indicators = report.calculate_impact_indicators()
        return {
            'project': project,
            'report': report,
            'performance_indicators': performance_indicators,
            'performance_indicator_mapping': tuple_to_dict_list(
                ('title', 'group'),
                constants.PERFORMANCE_INDICATOR_REPORTS[
                    report.report_data[constants.XFORM_ID]])
        }

from pyramid.view import (
    view_config,
    view_defaults,
)

from wkcdd.models.project import (
    ProjectType
)
from wkcdd import constants
from wkcdd.libs import utils


@view_defaults(route_name='projects')
class ProjectViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='projects',
                 renderer='projects.jinja2')
    def list_projects(self):
        #TODO fetch all raw data and save to tables to process key indicators
        project_types = ProjectType.all()

        #import data to projects table
        raw_data = utils.fetch_data(constants.DAIRY_COWS_PROJECT_REGISTRATION)
        utils.populate_projects_table(raw_data)

        #import data to reports table
        utils.populate_reports_table(constants.DAIRY_COWS_PROJECT_REPORT)
        return {
            'project_types': project_types,
            'response': raw_data
        }

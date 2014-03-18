import requests
import json
from pyramid.view import (
    view_config,
    view_defaults,
)

from wkcdd.models.project import (
    Project,
    ProjectType
)
from wkcdd.models.form import(
    Form
)


@view_defaults(route_name='projects')
class ProjectViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='projects',
                 renderer='projects.jinja2')
    def list_projects(self):
        #TODO fetch all raw data and save to tables to process key indicators
        project_types = ProjectType.all()
        registration_form_id = Form.get_registration_form_id()
        headers = {'Authorization': 'Token 1142ea373ff4bcf894e83ef76ef8c99d3e5fb587'}
        ona_rest_api = 'https://ona.io/api/v1/data/wkcdd/'
        form_data_url = ona_rest_api + registration_form_id
        response = requests.get(
            form_data_url,
            headers=headers)

        raw_data = json.loads(response.content)

        return {
            'project_types': project_types,
            'response': raw_data
        }

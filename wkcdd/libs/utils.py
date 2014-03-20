import requests
import datetime
from sqlalchemy.orm.exc import NoResultFound
from wkcdd.models import Community, Location, Report, Project
from wkcdd.models.project import ProjectType
from wkcdd import constants


def fetch_data(form_id):
    headers = {'Authorization':
               'Token 1142ea373ff4bcf894e83ef76ef8c99d3e5fb587'
               }
    ona_rest_api = 'https://ona.io/api/v1/data/wkcdd/'
    onadata_url = ona_rest_api + form_id
    response = requests.get(onadata_url, headers=headers)

    if response.status_code != 200:
        raise Exception("Server responded with %s" % response.status_code)

    raw_data = response.json()
    return raw_data


def populate_projects_table(raw_data):
    for projects_data in raw_data:
        # register project
        add_project(projects_data)


def add_project(projects_data):
    project_code = projects_data.get(constants.PROJECT_CODE)
    project_name = projects_data.get(constants.PROJECT_NAME)
    constituency = Location.get_or_create(
        projects_data.get(constants.CONSTITUENCY), 'constituency')
    community = Community.get_or_create(
        projects_data.get(constants.COMMUNITY_NAME),
        constituency,
        projects_data.get(constants.GEOLOCATION)
    )
    projects_data.get(constants.PROJECT_TYPE)
    project_type = ProjectType.get_or_create(projects_data.get(constants.PROJECT_TYPE))

    Project.create(project_code=project_code,
                   name=project_name,
                   community_id=community.id,
                   project_type_id=project_type.id)


def populate_reports_table(raw_data):
    for report_data in raw_data:
            try:
                project = Project.get(
                    Project.code == report_data.get(constants.REPORT_PROJECT_CODE))
                report_submission = Report(
                    project_code=project.code,
                    submission_time=datetime.datetime.strptime(
                        report_data.get(constants.REPORT_SUBMISSION_TIME), "%Y-%m-%dT%H:%M:%S" ),
                    month=(report_data.get(constants.REPORT_MONTH)),
                    quarter=(report_data.get(constants.REPORT_QUARTER)),
                    period=(report_data.get(constants.REPORT_PERIOD)),
                    report_data=report_data
                )
                Report.add_report_submission(report_submission)
            except NoResultFound:
                return None

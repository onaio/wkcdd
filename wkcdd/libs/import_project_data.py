import transaction
import requests
import datetime
from wkcdd.models import Report, Project
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


def populate_projects_table(raw_data, project_code):
    for project_data in raw_data:
        # register project
        add_project(project_data, project_code)
        transaction.commit()


def add_project(project_data, project_code):
    return Project.create(
        project_code=project_data.get(project_code),
        name=project_data.get(constants.PROJECT_NAME),
        county=project_data.get(constants.COUNTY),
        sub_county=project_data.get(constants.SUB_COUNTIES),
        constituency=project_data.get(constants.CONSTITUENCY),
        community_name=project_data.get(constants.COMMUNITY_NAME),
        geolocation=project_data.get(constants.GEOLOCATION),
        project_type=project_data.get(constants.PROJECT_TYPE),
        sector=constants.PROJECT_SECTORS[project_data.get(constants.XFORM_ID)]
    )


def populate_reports_table(raw_data, project_report_code):
    for report_data in raw_data:
        report_submission = Report(
            project_code=report_data.get(project_report_code),
            submission_time=datetime.datetime.strptime(
                report_data.get(constants.REPORT_SUBMISSION_TIME),
                "%Y-%m-%dT%H:%M:%S"),
            month=report_data.get(constants.REPORT_MONTH),
            quarter=report_data.get(constants.REPORT_QUARTER),
            period=report_data.get(constants.REPORT_PERIOD),
            report_data=report_data
        )
        Report.add_report_submission(report_submission)
        #transaction.commit()


# fetch project registration data and persist it to the DB
def fetch_project_registration_data():
    for project_registration_form, project_code\
            in constants.PROJECT_REGISTRATION_FORMS:
        populate_projects_table(fetch_data(project_registration_form),
                                project_code)


# fetch project report data and persist it to the DB
def fetch_report_form_data():
    for project_report_form, project_report_code\
            in constants.PROJECT_REPORT_FORMS:
        populate_reports_table(fetch_data(project_report_form),
                               project_report_code)

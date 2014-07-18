import transaction
import requests
import datetime
import csv

from wkcdd.models import Report, Project
from wkcdd.models import (
    Location,
    Community,
    County,
    SubCounty,
    Constituency)
from wkcdd.models.project import ProjectType
from wkcdd import constants

COUNTY = 'county'
SUB_COUNTY = 'sub_county'
CONSTITUENCY = 'constituency'
COMMUNITY = 'community'
LONGITUDE = 'long'
LATITUDE = 'lat'
SECTOR = 'sector'

OLD_PROJECT_FILE = 'data/old_projects.csv'
NEW_PROJECT_FILE = 'data/new_projects.csv'


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
        project_data=project_data,
        sector=project_data.get(constants.XFORM_ID)
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
            status='approved',
            report_data=report_data
        )
        Report.add_report_submission(report_submission)


# fetch project registration data and persist it to the DB
def fetch_project_registration_data():
    for project_registration_form, project_code\
            in constants.PROJECT_REGISTRATION_FORMS:
            with transaction.manager:
                populate_projects_table(fetch_data(project_registration_form),
                                        project_code)


# fetch project report data and persist it to the DB
def fetch_report_form_data():
    for project_report_form, project_report_code\
            in constants.PROJECT_REPORT_FORMS:
        with transaction.manager:
            populate_reports_table(fetch_data(project_report_form),
                                   project_report_code)


def add_old_project_data(column_mapping, project_import_rows):
    with transaction.manager:
        for row in project_import_rows:
            # create location or get id of existing one
            project_type = row[column_mapping[constants.PROJECT_TYPE]].upper()
            sector = row[column_mapping[SECTOR]]
            start_date = row[column_mapping[constants.PROJECT_START_DATE]]
            name = row[column_mapping[constants.PROJECT_NAME]]

            # Exclude project_types that are not CAP or YAP
            # or those whose sectors are not defined
            if project_type in ['CAP', 'YAP'] and sector != 'none' \
                    and start_date:
                county = County.get_or_create(
                    row[column_mapping[COUNTY]], None, Location.COUNTY)
                sub_county = SubCounty.get_or_create(
                    row[column_mapping[SUB_COUNTY]],
                    county,
                    Location.SUB_COUNTY)
                constituency = Constituency.get_or_create(
                    row[column_mapping[CONSTITUENCY]],
                    sub_county,
                    Location.CONSTITUENCY)
                community = Community.get_or_create(
                    row[column_mapping[COMMUNITY]],
                    constituency,
                    Location.COMMUNITY)
                project_type = ProjectType.get_or_create(project_type)

                project_data = {
                    constants.PROJECT_START_DATE: (
                        start_date),
                    constants.PROJECT_CHAIRPERSON: (
                        row[column_mapping[constants.PROJECT_CHAIRPERSON]]),
                    constants.PROJECT_CHAIRPERSON_PHONE: (
                        row[column_mapping[
                            constants.PROJECT_CHAIRPERSON_PHONE]]),
                    constants.PROJECT_SECRETARY: (
                        row[column_mapping[constants.PROJECT_SECRETARY]]),
                    constants.PROJECT_SECRETARY_PHONE: (
                        row[column_mapping[
                            constants.PROJECT_SECRETARY_PHONE]]),
                    constants.PROJECT_TREASURER: (
                        row[column_mapping[constants.PROJECT_TREASURER]]),
                    constants.PROJECT_TREASURER_PHONE: (
                        row[column_mapping[constants.PROJECT_TREASURER_PHONE]])
                }
                # needs to be generated
                project = Project(code='',
                                  name=name,
                                  community_id=community.id,
                                  project_type_id=project_type.id,
                                  sector=sector,
                                  geolocation="{} {} ".format(
                                      row[column_mapping[LATITUDE]],
                                      row[column_mapping[LONGITUDE]]),
                                  project_data=project_data)
                project.save()


def import_legacy_data(import_file_url):
    if import_file_url is None:
        raise ValueError("File url not provided")

    project_import_rows = []

    with open(import_file_url, 'rbU') as csvfile:
        reader = csv.reader(csvfile)
        # Ignore first row
        column_headers = reader.next()
        column_mapping = {
            header: index
            for index, header in enumerate(column_headers)}
        for row in reader:
            project_import_rows.append(row)

    add_old_project_data(column_mapping, project_import_rows)

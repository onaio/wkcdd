import requests
import json
import datetime

from wkcdd.models.report import Report
from wkcdd import constants


def fetch_data(form_id):
    headers = {'Authorization':
               'Token 1142ea373ff4bcf894e83ef76ef8c99d3e5fb587'
               }
    ona_rest_api = 'https://ona.io/api/v1/data/wkcdd/'
    onadata_url = ona_rest_api + form_id
    response = requests.get(onadata_url, headers=headers)
    raw_data = json.loads(response.content)
    return raw_data


def populate_reports_table(report_form_id, raw_data):
    for report_data in raw_data:
            project_code = report_data.get(constants.PROJECT_CODE)
            report_submission = Report(
                project_id=project_code,
                report_date=datetime.datetime(2014, 3, 1),
                report_data=report_data,
                form_id=report_form_id
            )
            Report.add_report_submission(report_submission)

import os
import json
import unittest
import transaction
import datetime

from pyramid.registry import Registry
from pyramid import testing
from pyramid.paster import (
    get_appsettings
)
from pyramid.security import IAuthenticationPolicy
from sqlalchemy import engine_from_config
from webtest import TestApp

from wkcdd import main
from wkcdd.models.base import (
    DBSession,
    Base)
from wkcdd.models.location import (
    Location,
    LocationType
)
from wkcdd.models.project import(
    Project,
    ProjectType
)
from wkcdd.models.community import(
    Community
)
from wkcdd.models.form import (
    Form,
    FormTypes
)
from wkcdd.models.report import (
    Report
)

SETTINGS_FILE = 'test.ini'
settings = get_appsettings(SETTINGS_FILE)
engine = engine_from_config(settings, 'sqlalchemy.')


def _load_json_fixture(path):

    return json.load(open(path, 'r'))


class TestBase(unittest.TestCase):
    test_dir = os.path.realpath(os.path.dirname(__file__))
    project_submission = _load_json_fixture(os.path.join(
        os.path.dirname(__file__), 'fixtures', 'project_submission.json'))

    report_submission = _load_json_fixture(os.path.join(
        os.path.dirname(__file__), 'fixtures', 'report_submission.json'))

    def setUp(self):
        registry = Registry()
        registry.settings = settings
        self.config = testing.setUp(registry=registry)
        # setup db
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine
        Base.metadata.drop_all()
        Base.metadata.create_all()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def _add_project(self,
                     project_code='FR3A',
                     name='Dairy Cow Project Center 1',
                     community=None,
                     project_type=None):
        project = Project(
            code=project_code,
            name=name,
            community=community,
            project_type=project_type,
            sector="Dairy Goat",
            geolocation="0.0 0.0"
        )

        project.save()

        return project

    def _add_location_type(self, name="constituency"):

        location_type = LocationType(name=name)

        location_type.save()

        return location_type

    def _add_location(self, name="Kakamega", parent_id=0,
                      location_type=1):
        location = Location(
            name=name, parent_id=parent_id, location_type=location_type)

        location.save()

        return location

    def _add_project_type(self, name="Dairy Cow Project"):
        project_type = ProjectType(name=name)
        project_type.save()

        return project_type

    def _add_community(self, name="Bukusu", constituency=None):
        community = Community(name=name, constituency=constituency)

        community.save()

        return community

    def _add_form_types(self, name='registration'):
        form_type = FormTypes(name=name)

        form_type.save()

        return form_type

    def _add_form(self, form_id="dairy_cow_form_registration",
                  form_name="Dairy Cow Registration",
                  project_type_id=1,
                  form_type_id=1,
                  form_data="{'data':test}"):
        form = Form(form_id=form_id, form_name=form_name,
                    project_type_id=project_type_id,
                    form_type_id=form_type_id,
                    form_data=form_data)

        form.save()

        return form

    def _add_report(self, project_code="FR3A",
                    submission_time=datetime.datetime(2014, 3, 1),
                    month=3, quarter='q_2', period='2013_14',
                    report_data="{'data':test_report}"):
        report = Report(project_code=project_code, report_data=report_data,
                        submission_time=submission_time, month=month,
                        quarter=quarter, period=period)
        report.save()

        return report

    def _save_to_db(self, obj):
        with transaction.manager:
            DBSession.add(obj)
            DBSession.flush()

    def setup_test_data(self):
        self._add_location_type()
        self._add_location_type(name="sub_county")
        self._add_location_type(name="county")

        county = self._add_location(name="Bungoma",
                                    parent_id=0,
                                    location_type=3)

        sub_county = self._add_location(name="Bungoma",
                                        parent_id=county.id,
                                        location_type=2)

        constituency1 = self._add_location(name="Kakamega",
                                           parent_id=sub_county.id,
                                           location_type=1)

        self._add_location(name="Busia",
                           parent_id=0,
                           location_type=3)

        project_type_c = self._add_project_type(name="Dairy Cow Project")
        project_type_g = self._add_project_type(name="Dairy Goat Project")

        community1 = self._add_community(name="Maragoli",
                                         constituency=constituency1)

        community2 = self._add_community(name="Bukusu",
                                         constituency=constituency1)

        self._add_project(community=community1,
                          project_type=project_type_c)
        self._add_project(project_code="YH9T",
                          name="Dairy Goat Project Center 1",
                          community=community2,
                          project_type=project_type_g
                          )
        self._add_project(project_code="JDCV",
                          name="Dairy Goat Project Center 2",
                          community=community2,
                          project_type=project_type_g
                          )
        self._add_project(project_code="WRTD",
                          name="Dairy Goat Project Center 2",
                          community=community2,
                          project_type=project_type_g
                          )

        self._add_form_types(name="registration")
        self._add_form_types(name="registration")

        self._add_form()
        self._add_form(
            form_id="dairy_cow_form_report",
            form_name="Dairy Cow Report",
            project_type_id=1,
            form_type_id=2,
            form_data="{'data':test}")

        report_data_1 = _load_json_fixture(os.path.join(
            self.test_dir, 'fixtures', 'YH9T.json'))
        report_data_2 = _load_json_fixture(os.path.join(
            self.test_dir, 'fixtures', 'JDCV.json'))
        report_data_3 = _load_json_fixture(os.path.join(
            self.test_dir, 'fixtures', 'KYJ7.json'))
        report_data_4 = _load_json_fixture(os.path.join(
            self.test_dir, 'fixtures', 'YHCX.json'))
        report_data_5 = _load_json_fixture(os.path.join(
            self.test_dir, 'fixtures', 'DRT4.json'))

        self._add_report(project_code='YH9T', report_data=report_data_1)
        self._add_report(project_code='JDCV', report_data=report_data_2)
        self._add_report(project_code='KYJ7', report_data=report_data_3)
        self._add_report(project_code='YHCX', report_data=report_data_4)
        self._add_report(project_code='DRT4', report_data=report_data_5)
        self._add_report(project_code='WRTD',
                         report_data=report_data_3,
                         submission_time=datetime.datetime(2014, 3, 21))
        self._add_report(project_code='WRTD',
                         report_data=report_data_3,
                         submission_time=datetime.datetime(2014, 3, 12))
        self._add_report(project_code='WRTD',
                         report_data=report_data_3,
                         submission_time=datetime.datetime(2014, 3, 10))


class IntegrationTestBase(TestBase):
    def setUp(self):
        super(IntegrationTestBase, self).setUp()
        self.config.include('wkcdd')


class FunctionalTestBase(IntegrationTestBase):
    def _login_user(self, userid):
        policy = self.testapp.app.registry.queryUtility(IAuthenticationPolicy)
        headers = policy.remember(self.request, userid)
        cookie_parts = dict(headers)['Set-Cookie'].split('; ')
        cookie = filter(
            lambda i: i.split('=')[0] == 'auth_tkt', cookie_parts)[0]
        return {'Cookie': cookie}

    def setUp(self):
        super(FunctionalTestBase, self).setUp()
        current_dir = os.getcwd()
        app = main(
            {
                '__file__': os.path.join(current_dir, SETTINGS_FILE),
                'here': current_dir
            },
            **settings)
        self.testapp = TestApp(app)
        self.request = testing.DummyRequest()
        self.request.environ = {
            'SERVER_NAME': 'example.com',
        }

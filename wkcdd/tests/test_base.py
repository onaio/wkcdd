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
from wkcdd.models.project import(
    Project,
    ProjectType
)
from wkcdd.models.form import (
    Form,
    FormTypes
)
from wkcdd.models.report import (
    Report
)

from wkcdd.models.constituency import Constituency
from wkcdd.models.county import County
from wkcdd import constants
from wkcdd.models import (
    Community,
    SubCounty
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
                     name='Dairy Goat Project Center 1',
                     community=None,
                     sector=constants.DAIRY_GOAT_PROJECT_REGISTRATION,
                     project_type=None,
                     project_data='{code:"FR3A"}',
                     geolocation="0.0 0.0 0 0"):
        project = Project(
            code=project_code,
            name=name,
            community=community,
            project_type=project_type,
            sector=sector,
            geolocation=geolocation
        )

        project.save()

        return project

    def _add_county(self, name="Kakamega"):
        location = County(name=name)

        location.save()
        return location

    def _add_sub_county(self, county, name="Kakamega"):
        location = SubCounty(name=name, county=county)

        location.save()
        return location

    def _add_constituency(self, sub_county, name="Constituency"):
        constituency = Constituency(name=name, sub_county=sub_county)

        constituency.save()

        return constituency

    def _add_community(self, constituency, name="Community"):
        community = Community(name=name, constituency=constituency)

        community.save()

        return community

    def _add_project_type(self, name="Dairy Cow Project"):
        project_type = ProjectType(name=name)

        project_type.save()

        return project_type

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
                    status=Report.APPROVED,
                    report_data="{'data':test_report}"):
        report = Report(project_code=project_code, report_data=report_data,
                        submission_time=submission_time, month=month,
                        quarter=quarter, period=period, status=status)
        report.save()

        return report

    def _save_to_db(self, obj):
        with transaction.manager:
            DBSession.add(obj)
            DBSession.flush()

    def setup_test_data(self):
        transaction.begin()
        """
          ### Locations
          Bungoma county -> Bungoma Sub County -> Kakamega Const ->
            Maragoli Community, Bukusu Community

          Busia County -> Teso Sub County -> Amagoro Const -> Rwatama

          Siaya County
        """
        county = self._add_county(name="Bungoma")
        county3 = self._add_county(name="Siaya")  # noqa

        sub_county = self._add_sub_county(county=county, name="Bungoma")

        constituency1 = self._add_constituency(
            sub_county=sub_county, name="Kakamega")

        county2 = self._add_county(name="Busia")
        sub_county2 = self._add_sub_county(county=county2, name="Teso")
        constituency3 = self._add_constituency(
            sub_county=sub_county2, name="Amagoro")
        community3 = self._add_community(
            constituency=constituency3, name="Rwatama")

        project_type_c = self._add_project_type(name="Dairy Cow Project")
        project_type_g = self._add_project_type(name="Dairy Goat Project")

        community1 = self._add_community(
            constituency=constituency1, name="Maragoli")

        community2 = self._add_community(
            constituency=constituency1, name="Bukusu")

        self._add_project(community=community1,
                          project_type=project_type_c)
        self._add_project(project_code='7CWA',
                          name="Dairy Cow Project Center 1",
                          community=community1,
                          sector=constants.DAIRY_COWS_PROJECT_REGISTRATION,
                          project_type=project_type_c
                          )
        self._add_project(project_code="YH9T",
                          name="Dairy Cow Project Center 1",
                          community=community2,
                          sector=constants.DAIRY_COWS_PROJECT_REGISTRATION,
                          project_type=project_type_c,
                          geolocation=""
                          )
        self._add_project(project_code="JDCV",
                          name="Dairy Goat Project Center 2",
                          community=community2,
                          project_type=project_type_g
                          )
        self._add_project(project_code="WRTD",
                          name="Dairy Goat Project Center 3",
                          community=community2,
                          project_type=project_type_g,
                          geolocation="0.1231 34.1213 1562 5"
                          )
        self._add_project(project_code="NOREPORT",
                          name="Dairy Goat Project Center 4",
                          community=community2,
                          project_type=project_type_g
                          )
        self._add_project(project_code="WRXT",
                          name="Dairy Goat Project Center 5",
                          community=community3,
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
        report_data_6 = _load_json_fixture(os.path.join(
            self.test_dir, 'fixtures', '7CWA.json'))

        self._add_report(project_code='YH9T', report_data=report_data_1)
        self._add_report(project_code='JDCV', report_data=report_data_2)
        self._add_report(project_code='KYJ7', report_data=report_data_3)
        self._add_report(project_code='YHCX', report_data=report_data_4)
        self._add_report(project_code='DRT4', report_data=report_data_5)
        self._add_report(project_code='7CWA', report_data=report_data_6)
        self._add_report(project_code='WRTD',
                         report_data=report_data_3,
                         submission_time=datetime.datetime(2014, 3, 21))
        self._add_report(project_code='WRTD',
                         report_data=report_data_3,
                         submission_time=datetime.datetime(2014, 3, 12))
        self._add_report(project_code='WRTD',
                         report_data=report_data_3,
                         submission_time=datetime.datetime(2014, 3, 10))
        self._add_report(project_code='WRXT',
                         report_data=report_data_4,
                         status=Report.PENDING,
                         submission_time=datetime.datetime(2014, 3, 10))
        transaction.commit()

    def setup_community_test_data(self):
        transaction.begin()
        county = self._add_county(name="Bungoma")

        sub_county = self._add_sub_county(county=county, name="Bungoma")

        constituency = self._add_constituency(
            sub_county=sub_county, name="sirisia")
        community = self._add_community(
            constituency=constituency, name="lutacho")
        project_type = self._add_project_type(name="CAP")
        self._add_project(project_code="COW1",
                          name="Cow project 1",
                          community=community,
                          project_type=project_type,
                          sector=constants.DAIRY_COWS_PROJECT_REGISTRATION
                          )
        self._add_project(project_code="COW2",
                          name="Cow project 2",
                          community=community,
                          project_type=project_type,
                          sector=constants.DAIRY_COWS_PROJECT_REGISTRATION
                          )
        self._add_project(project_code="GOAT1",
                          name="Goat project 1",
                          community=community,
                          project_type=project_type,
                          sector=constants.DAIRY_GOAT_PROJECT_REGISTRATION
                          )
        self._add_project(project_code="BODA1",
                          name="Bodaboda project 1",
                          community=community,
                          project_type=project_type,
                          sector=constants.BODABODA_PROJECT_REGISTRATION
                          )
        transaction.commit()

    def setup_report_period_test_data(self):
        """
        Report months Jan, May, Aug, Dec
        Report quarters q_1, q_2, q_3, q_4
        Reporting years 2012_2013, 2013_2014
        """

        transaction.begin()

        county = self._add_county(name="Bungoma")
        sub_county = self._add_sub_county(county=county, name="Bungoma")
        constituency = self._add_constituency(
            sub_county=sub_county, name="Bumula")
        community = self._add_community(
            constituency=constituency, name="Kibuke")

        project_type = self._add_project_type(name="CAP")

        self._add_project(project_code="7CWA",
                          name="Cow project 1",
                          project_type=project_type,
                          community=community,
                          sector=constants.DAIRY_COWS_PROJECT_REGISTRATION
                          )
        months = ['1', '5', '8', '12']
        quarters = ['q_1', 'q_2', 'q_3', 'q_4']
        reporting_years = ['2012_13', '2013_14']

        report_data = _load_json_fixture(os.path.join(
            self.test_dir, 'fixtures', '7CWA.json'))

        for index, month in enumerate(months, 0):
            # Jan(1) and May(2) will be in year 2012_13
            # Aug(8) and Dec(12) will be in year 2013_14
            year = reporting_years[0] if index < 2 else reporting_years[1]
            self._add_report(project_code='7CWA',
                             report_data=report_data,
                             submission_time=datetime.datetime(2014, 3, 1),
                             month=month,
                             quarter=quarters[index],
                             period=year)

        transaction.commit()


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

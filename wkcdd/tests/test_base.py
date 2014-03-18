import os
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


class TestBase(unittest.TestCase):
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

    def setup_test_data(self):
        location_type1 = LocationType(id=1, name="constituency")
        location_type2 = LocationType(id=2, name="sub-county")
        location_type3 = LocationType(id=3, name="county")
        with transaction.manager:
            DBSession.add_all([location_type1,
                               location_type2,
                               location_type3])

        location1 = Location(name="Kakamega",
                             parent_id=0,
                             location_type=1)
        location2 = Location(name="Bungoma",
                             parent_id=0,
                             location_type=2)
        location3 = Location(name="Busia",
                             parent_id=0,
                             location_type=3)
        with transaction.manager:
            DBSession.add_all([location1, location2, location3])

        project_type1 = ProjectType(id=1,
                                    name="Dairy Cow Project"
                                    )
        project_type2 = ProjectType(id=2,
                                    name="Dairy Goat Project"
                                    )
        with transaction.manager:
            DBSession.add_all([project_type1, project_type2])

        community1 = Community(id=1,
                               name="Maragoli",
                               constituency_id=1,
                               geolocation="Lat 0.0, Long 0.0")

        community2 = Community(id=2,
                               name="Bukusu",
                               constituency_id=2,
                               geolocation="Lat 0.0, Long 0.0")
        with transaction.manager:
            DBSession.add_all([community1, community2])

        project1 = Project(project_code="FR3A",
                           name="Dairy Cow Project Center 1",
                           community_id=1,
                           project_type_id=1
                           )
        project2 = Project(project_code="YH9T",
                           name="Dairy Goat Project Center 1",
                           community_id=2,
                           project_type_id=2
                           )
        with transaction.manager:
            DBSession.add_all([project1, project2])

        form_type1 = FormTypes(id=1,
                               name="registration")
        form_type2 = FormTypes(id=2,
                               name="registration")
        with transaction.manager:
            DBSession.add_all([form_type1, form_type2])

        form1 = Form(form_id="dairy_cow_form_registration",
                     form_name="Dairy Cow Registration",
                     project_type_id=1,
                     form_type_id=1,
                     form_data="{'data':test}")

        form2 = Form(form_id="dairy_cow_form_report",
                     form_name="Dairy Cow Report",
                     project_type_id=1,
                     form_type_id=2,
                     form_data="{'data':test}")
        with transaction.manager:
            DBSession.add_all([form1, form2])

        report = Report(project_id="FR3A",
                        report_date=datetime.datetime(2014, 3, 1),
                        report_data="{'data':test_report}",
                        form_id="dairy_cow_form_report")
        with transaction.manager:
            DBSession.add_all([report])


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

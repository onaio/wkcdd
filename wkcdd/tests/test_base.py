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
    submissions = [
        # project submissions
            '{"sector": "dairy", "cp_phone": "0725385308", "signature_treasurer": "1390477712313.jpg", "_bamboo_dataset_id": "", "_tags": [], "county": "eshibuli", "_xform_id_string": "dairy_cows_project_registration3", "chair": "Desterio Ndunde", "meta/instanceID": "uuid:c8c57c95-03cd-4c7b-9fb0-4840e1d57c3c", "p_name": "Dairy Cows", "county_sub_counties": "kakamega", "end": "2014-01-23T15:33:45.405+03", "number_treas": "07202000624", "start": "2014-01-23T14:36:30.333+03", "county_contituency": "lurambi", "_status": "submitted_via_web", "formhub/uuid": "867ac75ff99f409d9b558f1792b62a14", "start_date": "2013-01-10", "_geolocation": ["0.28092078776349744", "34.6476717774632"], "sec_phone": "0720248940", "_uuid": "c8c57c95-03cd-4c7b-9fb0-4840e1d57c3c", "signature_chair": "1390477766697.jpg", "treasurer": "Florence Akaliche", "group_photo": "1390480154267.jpg", "project_location": "0.28092078776349744 34.6476717774632 1370.0 5.0", "dc_projects": "NYUW", "projecttype": "cap", "_submission_time": "2014-01-27T14:19:03", "_notes": [], "_attachments": [], "_id": 28534, "county_counties": "kakamega", "signature_sec": "1390477813806.jpg", "secretary": "Isaac Aura"}'
    ]

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
        project3 = Project(project_code="TGIF",
                           name="Dairy Cow Center 2",
                           community_id=2,
                           project_type_id=1
                           )
        with transaction.manager:
            DBSession.add_all([project1, project2, project3])

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

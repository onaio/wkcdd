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
    project_submission = [
        # project submissions
            '{"sector": "dairy", "cp_phone": "0725385308", "signature_treasurer": "1390477712313.jpg", "_bamboo_dataset_id": "", "_tags": [], "county": "eshibuli", "_xform_id_string": "dairy_cows_project_registration3", "chair": "Desterio Ndunde", "meta/instanceID": "uuid:c8c57c95-03cd-4c7b-9fb0-4840e1d57c3c", "p_name": "Dairy Cows", "county_sub_counties": "kakamega", "end": "2014-01-23T15:33:45.405+03", "number_treas": "07202000624", "start": "2014-01-23T14:36:30.333+03", "county_contituency": "lurambi", "_status": "submitted_via_web", "formhub/uuid": "867ac75ff99f409d9b558f1792b62a14", "start_date": "2013-01-10", "_geolocation": ["0.28092078776349744", "34.6476717774632"], "sec_phone": "0720248940", "_uuid": "c8c57c95-03cd-4c7b-9fb0-4840e1d57c3c", "signature_chair": "1390477766697.jpg", "treasurer": "Florence Akaliche", "group_photo": "1390480154267.jpg", "project_location": "0.28092078776349744 34.6476717774632 1370.0 5.0", "dc_projects": "NYUW", "projecttype": "cap", "_submission_time": "2014-01-27T14:19:03", "_notes": [], "_attachments": [], "_id": 28534, "county_counties": "kakamega", "signature_sec": "1390477813806.jpg", "secretary": "Isaac Aura"}'
    ]

    report_submission =[
        '{\
            "perfomance_summary/month": "12","meetings/epmc_expected_members": "5","perfomance_summary/exp_contribution": "624800","meetings/agm_mh": "1","_tags": [],"meetings/mmm_mh": "4","membership/f_members": "113","photo_signatures/date_compiled": "2014-01-03","mproject_performance/milk_grp_sale_target": "162000","perfomance_summary/quarter_year": "q_2","meetings/agm_em": "1","mproject_performance/milk_grp_sale_percentage": "32","mproject_performance/vb_percentage": "12","membership/v_pmc_members": "2","mproject_performance/fb_target": "50","meetings/agm_expected_members": "158","perfomance_summary/sub_county": "bwake","perfomance_summary/community_contribution": "100","_submission_time": "2014-01-06T20:14:03","mproject_performance/msold_bnf_target": "900","_geolocation": [null,null],"mproject_performance/vb_target": "25","membership/total_pmc_members": "5","photo_signatures/sec_name": "dorcus kwoba","mproject_performance/recommendations": "none","meetings/epmc_ma_percentage": "80","meta/instanceID": "uuid:1b16b923-2ef6-4260-a5d0-f0fa87133980","mproject_performance/msold_bnf_percentage": "43","mproject_performance/ai_target": "0","meetings/spm_em": "1","mproject_performance/ai_percentage": "0","perfomance_summary/sub_county_counties": "bungoma","_uuid": "1b16b923-2ef6-4260-a5d0-f0fa87133980","meetings/agm_ma_percentage": "40","membership/v_members": "29","mproject_performance/funds_expenditure_percentage": "93",\
            "meetings/mmm_members_attended": "59",\
            "photo_signatures/signature_sec": "1388756715105.jpg","mproject_performance/cws_proceeds_percentage": "22",\
            "perfomance_summary/sub_county_contituency": "sirisia","meetings/epmc_mh": "2",\
            "mproject_performance/db_achievement": "13","meetings/mmm_em": "3","photo_signatures/project_photo": "1389028956789.jpg",\
            "mproject_performance/funds_recieved": "778200","mproject_performance/msold_bnf_achievement": "390",\
            "mproject_performance/vb_achievement": "3","meetings/epmc_em": "3","_notes": [],\
            "mproject_performance/expected_funds": "778200","_bamboo_dataset_id": "",\
            "mproject_performance/cr_achievement": "5","meetings/agm_members_attended": "63",\
            "meetings/agm_mh_percentage": "100","mproject_performance/cows_target": "12",\
            "mproject_performance/funds_recieved_percentage": "100","start": "2014-01-03T16:32:34.533+03",\
            "mproject_performance/milk_grp_sale_achievement": "51200",\
            "perfomance_summary/year": "2013_14","mproject_performance/cr_target": "48",\
            "mproject_performance/milk_bnf_sale_achievement": "5850","_status": "submitted_via_web",\
            "mproject_performance/observations": "none","mproject_performance/cws_proceeds_achievement": "34",\
            "photo_signatures/signature_chair": "1389029036914.jpg","mproject_performance/cows_percentage": "100",\
            "mproject_performance/m_acquired_percentage": "48",\"meetings/mmm_mh_percentage": "133",\
            "mproject_performance/mb_percentage": "8","mproject_performance/cows_achievement": "12",\
            "mproject_performance/m_acquired_achievement": "480","perfomance_summary/actual_contribution": "624800",\
            "meetings/mmm_ma_percentage": "37","membership/m_pmc_members": "2","meetings/epmc_mh_percentage": "67",\
            "_attachments": [],"perfomance_summary/sub_county_sub_counties": "bungoma",\
            "end": "2014-01-06T20:24:27.581+03","mproject_performance/milk_bnf_sale_target": "9000",\
            "membership/total_members": "158","photo_signatures/admin_change": "no",\
            "mproject_performance/db_percentage": "10","mproject_performance/m_acquired_target": "990",\
            "perfomance_summary/dc_projects": "FR3A","mproject_performance/mb_achievement": "7",\
            "mproject_performance/cws_proceeds_target": "158","membership/f_pmc_members": "3",\
            "mproject_performance/mb_target": "85","perfomance_summary/project_type": "cap",\
            "mproject_performance/milk_bnf_sale_percentage": "65","photo_signatures/chair_person": "Edward Muliro",\
            "mproject_performance/cr_percentage": "10","formhub/uuid": "e3990ef556ff40b0912ad776be814ff9",\
            "meetings/epmc_members_attended": "4","mproject_performance/funds_expenditure": "723500","register": "yes",\
            "mproject_performance/fb_achievement": "6","mproject_performance/db_target": "135",\
            "mproject_performance/fb_percentage": "12","mproject_performance/ai_achievement": "0",\
            "membership/m_members": "45","_xform_id_string": "dairy_cows_project_report",\
            "meetings/mmm_expected_members": "158","_id": 28519\
        }',
        '{\
            "perfomance_summary/month": "12","meetings/epmc_expected_members": "5","perfomance_summary/exp_contribution": "624800","meetings/agm_mh": "1","_tags": [],"meetings/mmm_mh": "4","membership/f_members": "113","photo_signatures/date_compiled": "2014-01-03","mproject_performance/milk_grp_sale_target": "162000","perfomance_summary/quarter_year": "q_2","meetings/agm_em": "1","mproject_performance/milk_grp_sale_percentage": "32","mproject_performance/vb_percentage": "12","membership/v_pmc_members": "2","mproject_performance/fb_target": "50","meetings/agm_expected_members": "158","perfomance_summary/sub_county": "bwake","perfomance_summary/community_contribution": "100","_submission_time": "2014-01-06T20:14:03","mproject_performance/msold_bnf_target": "900","_geolocation": [null,null],"mproject_performance/vb_target": "25","membership/total_pmc_members": "5","photo_signatures/sec_name": "dorcus kwoba","mproject_performance/recommendations": "none","meetings/epmc_ma_percentage": "80","meta/instanceID": "uuid:1b16b923-2ef6-4260-a5d0-f0fa87133980","mproject_performance/msold_bnf_percentage": "43","mproject_performance/ai_target": "0","meetings/spm_em": "1","mproject_performance/ai_percentage": "0","perfomance_summary/sub_county_counties": "bungoma","_uuid": "1b16b923-2ef6-4260-a5d0-f0fa87133980","meetings/agm_ma_percentage": "40","membership/v_members": "29","mproject_performance/funds_expenditure_percentage": "93",\
            "meetings/mmm_members_attended": "59",\
            "photo_signatures/signature_sec": "1388756715105.jpg","mproject_performance/cws_proceeds_percentage": "22",\
            "perfomance_summary/sub_county_contituency": "sirisia","meetings/epmc_mh": "2",\
            "mproject_performance/db_achievement": "13","meetings/mmm_em": "3","photo_signatures/project_photo": "1389028956789.jpg",\
            "mproject_performance/funds_recieved": "778200","mproject_performance/msold_bnf_achievement": "390",\
            "mproject_performance/vb_achievement": "3","meetings/epmc_em": "3","_notes": [],\
            "mproject_performance/expected_funds": "778200","_bamboo_dataset_id": "",\
            "mproject_performance/cr_achievement": "5","meetings/agm_members_attended": "63",\
            "meetings/agm_mh_percentage": "100","mproject_performance/cows_target": "12",\
            "mproject_performance/funds_recieved_percentage": "100","start": "2014-01-03T16:32:34.533+03",\
            "mproject_performance/milk_grp_sale_achievement": "51200",\
            "perfomance_summary/year": "2013_14","mproject_performance/cr_target": "48",\
            "mproject_performance/milk_bnf_sale_achievement": "5850","_status": "submitted_via_web",\
            "mproject_performance/observations": "none","mproject_performance/cws_proceeds_achievement": "34",\
            "photo_signatures/signature_chair": "1389029036914.jpg","mproject_performance/cows_percentage": "100",\
            "mproject_performance/m_acquired_percentage": "48",\"meetings/mmm_mh_percentage": "133",\
            "mproject_performance/mb_percentage": "8","mproject_performance/cows_achievement": "12",\
            "mproject_performance/m_acquired_achievement": "480","perfomance_summary/actual_contribution": "624800",\
            "meetings/mmm_ma_percentage": "37","membership/m_pmc_members": "2","meetings/epmc_mh_percentage": "67",\
            "_attachments": [],"perfomance_summary/sub_county_sub_counties": "bungoma",\
            "end": "2014-01-06T20:24:27.581+03","mproject_performance/milk_bnf_sale_target": "9000",\
            "membership/total_members": "158","photo_signatures/admin_change": "no",\
            "mproject_performance/db_percentage": "10","mproject_performance/m_acquired_target": "990",\
            "perfomance_summary/dc_projects": "NOtThea","mproject_performance/mb_achievement": "7",\
            "mproject_performance/cws_proceeds_target": "158","membership/f_pmc_members": "3",\
            "mproject_performance/mb_target": "85","perfomance_summary/project_type": "cap",\
            "mproject_performance/milk_bnf_sale_percentage": "65","photo_signatures/chair_person": "Edward Muliro",\
            "mproject_performance/cr_percentage": "10","formhub/uuid": "e3990ef556ff40b0912ad776be814ff9",\
            "meetings/epmc_members_attended": "4","mproject_performance/funds_expenditure": "723500","register": "yes",\
            "mproject_performance/fb_achievement": "6","mproject_performance/db_target": "135",\
            "mproject_performance/fb_percentage": "12","mproject_performance/ai_achievement": "0",\
            "membership/m_members": "45","_xform_id_string": "dairy_cows_project_report",\
            "meetings/mmm_expected_members": "158","_id": 28519\
        }'

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

        project1 = Project(code="FR3A",
                           name="Dairy Cow Project Center 1",
                           community_id=1,
                           project_type_id=1
                           )
        project2 = Project(code="YH9T",
                           name="Dairy Goat Project Center 1",
                           community_id=2,
                           project_type_id=2
                           )
        project3 = Project(code="TGIF",
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

        report = Report(project_code="YH9T",
                        submission_time=datetime.datetime(2013, 3, 1),
                        month=3,
                        quarter='q_2',
                        period='2013_14',
                        report_data="{'data':test}"
                        )
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

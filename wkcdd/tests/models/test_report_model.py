import datetime
import json
from wkcdd.tests.test_base import TestBase
from wkcdd.models.report import Report


class TestReport(TestBase):
    def test_setup_test_data(self):
        self.setup_test_data()
        report = Report.get(Report.project_code == "YH9T")
        report_data = '{"perfomance_summary/month": "2", "meetings/epmc_expected_members": "5", "perfomance_summary/exp_contribution": "56000", "meetings/agm_mh": "0", "_tags": [], "impact_information/mb_target": "1", "meetings/mmm_mh": "3", "membership/f_members": "10", "perfomance_summary/dc_projects": "3TLN", "photo_signatures/date_compiled": "2014-03-19", "membership/m_members": "2", "perfomance_summary/quarter_year": "q_3", "meetings/agm_em": "1", "impact_information/vb_achievement": "4", "impact_information/no_children": "3", "mproject_performance/cows_achievement": "8", "membership/v_pmc_members": "3", "meetings/agm_expected_members": "13", "impact_information/milk_grp_sale_percentage": "30", "meetings/mmm_mh_percentage": "100", "perfomance_summary/community_contribution": "173", "_submission_time": "2014-03-19T16:15:01", "mproject_performance/msold_bnf_target": "12461", "_geolocation": [null, null], "impact_information/observations": "Good work", "photo_signatures/sec_name": "Linet isiche", "meetings/epmc_ma_percentage": "100", "meta/instanceID": "uuid:1be37a36-234d-44b9-994f-e6d030deead1", "mproject_performance/msold_bnf_percentage": "390", "impact_information/milk_grp_sale_achievement": "48000", "mproject_performance/ai_target": "8", "meetings/spm_em": "0", "impact_information/mb_achievement": "4", "impact_information/db_achievement": "10", "mproject_performance/ai_percentage": "38", "perfomance_summary/sub_county_counties": "busia", "_uuid": "1be37a36-234d-44b9-994f-e6d030deead1", "meetings/agm_ma_percentage": "0", "membership/v_members": "5", "mproject_performance/funds_expenditure_percentage": "239", "mproject_performance/cws_proceeds_target": "2", "photo_signatures/signature_sec": "1395222030924.jpg", "mproject_performance/cws_proceeds_percentage": "0", "impact_information/db_percentage": "77", "perfomance_summary/sub_county_contituency": "amagoro", "impact_information/b_improved_houses": "1", "impact_information/vb_target": "5", "meetings/epmc_mh": "3", "meetings/mmm_em": "3", "impact_information/b_income": "1", "mproject_performance/funds_recieved": "722930", "mproject_performance/msold_bnf_achievement": "48600", "meetings/epmc_em": "3", "_notes": [], "mproject_performance/expected_funds": "260630", "_bamboo_dataset_id": "", "membership/total_pmc_members": "5", "mproject_performance/cr_achievement": "6", "meetings/agm_members_attended": "0", "meetings/agm_mh_percentage": "0", "mproject_performance/cows_target": "10", "mproject_performance/funds_recieved_percentage": "277", "mproject_performance/cr_target": "14", "start": "2014-03-19T12:03:55.517+03", "impact_information/b_hh_assets": "3", "impact_information/milk_bnf_sale_achievement": "5400", "_status": "submitted_via_web", "impact_information/recommendations": "Support from the project", "mproject_performance/cws_proceeds_achievement": "0", "impact_information/fb_percentage": "50", "impact_information/fb_target": "12", "photo_signatures/signature_chair": "1395222005366.jpg", "mproject_performance/cows_percentage": "80", "mproject_performance/m_acquired_percentage": "30", "mproject_performance/m_acquired_achievement": "124", "perfomance_summary/actual_contribution": "96800", "meetings/mmm_ma_percentage": "100", "impact_information/milk_grp_sale_target": "162000", "membership/m_pmc_members": "1", "meetings/epmc_mh_percentage": "100", "perfomance_summary/sub_county_sub_counties": "teso", "end": "2014-03-19T12:41:08.474+03", "membership/total_members": "12", "photo_signatures/admin_change": "no", "impact_information/db_target": "13", "perfomance_summary/year": "2014-15", "perfomance_summary/sub_county": "agolot", "impact_information/vb_percentage": "80", "meetings/mmm_members_attended": "13", "membership/f_pmc_members": "4", "perfomance_summary/project_type": "cap", "impact_information/milk_bnf_sale_percentage": "43", "photo_signatures/chair_person": "Brigid Nakhabi", "mproject_performance/cr_percentage": "43", "formhub/uuid": "f74435756ba04c93a7ae0a5ef351d82f", "meetings/epmc_members_attended": "5", "impact_information/milk_bnf_sale_target": "12461", "mproject_performance/funds_expenditure": "623900", "register": "yes", "impact_information/fb_achievement": "6", "_attachments": ["wkcdd/attachments/1395222005366.jpg", "wkcdd/attachments/1395222030924.jpg"], "mproject_performance/ai_achievement": "3", "mproject_performance/m_acquired_target": "415", "_xform_id_string": "dairy_cows_project_report", "meetings/mmm_expected_members": "13", "_id": 36157, "impact_information/mb_percentage": "400"}'
        json_data = json.loads(report_data)
        self.assertEquals(report.report_data, json_data)

    def test_add_report_submission(self):
        self.setup_test_data()
        report_submission = Report(
            project_code="TGIF",
            submission_time=datetime.datetime(2013, 1, 1),
            month=3,
            quarter='q_2',
            period='2013_14',
            report_data="{'data':test}"
        )
        Report.add_report_submission(report_submission)
        report = Report.get(Report.project_code == "TGIF")

        self.assertEquals(report, report_submission)

    # Number of beneficiaries with increased income earned from the project
    def test_calculate_impact_indicator(self):
        self.setup_test_data()
        report = Report.get(Report.project_code == 'YH9T')
        impact_indicators = report.calculate_impact_indicators()
        self.assertEquals(impact_indicators['no_of_b_increased_income'],
                     '1')
        self.assertEquals(impact_indicators['no_of_b_improved_houses'],
                     '1')
        self.assertEquals(impact_indicators['no_of_b_hh_assets'],
                     '3')
        self.assertEquals(impact_indicators['no_of_children'],
                     '3')

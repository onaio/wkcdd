XFORM_ID = '_xform_id_string'

PROJECT_NAME = 'p_name'
PROJECT_TYPE = 'projecttype'
COMMUNITY_NAME = 'county'

COUNTY = 'county_counties'
SUB_COUNTIES = 'county_sub_counties'
CONSTITUENCY = 'county_contituency'

DATE_COMPILED = 'photo_signatures/date_compiled'
GEOLOCATION = 'project_location'

DAIRY_COWS_PROJECT_REGISTRATION = 'dairy_cows_project_registration3'
DAIRY_COWS_PROJECT_CODE = 'dc_projects'
DAIRY_COWS_PROJECT_REPORT = 'dairy_cows_project_report'
DAIRY_COWS_PROJECT_REPORT_CODE = 'perfomance_summary/dc_projects'

DAIRY_GOAT_PROJECT_REGISTRATION = 'dairy_goat_project_registration'
DAIRY_GOAT_PROJECT_CODE = 'dg_projects'
DAIRY_GOAT_PROJECT_REPORT = 'dairy_goat_project_report'
DAIRY_GOAT_PROJECT_REPORT_CODE = 'perfomance_summary/dg_projects'

FIC_PROJECT_REGISTRATION = \
    'field_industrial_crops_project_registration'
FIC_PROJECT_CODE = 'fic_projects'
FIC_PROJECT_REPORT = 'field_industrial_crop_project_report'
FIC_PROJECT_REPORT_CODE = 'perfomance_summary/fic_projects'

BODABODA_PROJECT_REGISTRATION = 'bodaboda_project_registration'
BODABODA_PROJECT_CODE = 'mct_projects'
BODABODA_PROJECT_REPORT = 'bodaboda_project_report'
BODABODA_PROJECT_REPORT_CODE = 'perfomance_summary/mct_projects'

POULTRY_PROJECT_REGISTRATION = 'poultry_project_registration'
POULTRY_PROJECT_CODE = 'poultry_projects'
POULTRY_PROJECT_REPORT = 'poultry_project_report'
POULTRY_PROJECT_REPORT_CODE = 'perfomance_summary/poultry_projects'

REPORT_SUBMISSION_TIME = '_submission_time'
REPORT_MONTH = 'perfomance_summary/month'
REPORT_QUARTER = 'perfomance_summary/quarter_year'
REPORT_PERIOD = 'perfomance_summary/year'

PROJECT_REGISTRATION_FORMS = (
    (DAIRY_GOAT_PROJECT_REGISTRATION, DAIRY_GOAT_PROJECT_CODE),
    (DAIRY_COWS_PROJECT_REGISTRATION, DAIRY_COWS_PROJECT_CODE),
    (FIC_PROJECT_REGISTRATION, FIC_PROJECT_CODE),
    (BODABODA_PROJECT_REGISTRATION, BODABODA_PROJECT_CODE),
    (POULTRY_PROJECT_REGISTRATION, POULTRY_PROJECT_CODE)
)

PROJECT_REPORT_FORMS = (
    (DAIRY_GOAT_PROJECT_REPORT, DAIRY_GOAT_PROJECT_REPORT_CODE),
    (DAIRY_COWS_PROJECT_REPORT, DAIRY_COWS_PROJECT_REPORT_CODE),
    (FIC_PROJECT_REPORT, FIC_PROJECT_REPORT_CODE),
    (BODABODA_PROJECT_REPORT, BODABODA_PROJECT_REPORT_CODE),
    (POULTRY_PROJECT_REPORT, POULTRY_PROJECT_REPORT_CODE)
)

PERFORMANCE_INDICATORS = {
    (DAIRY_GOAT_PROJECT_REPORT,
        ('perfomance_summary/exp_contribution',
         'perfomance_summary/actual_contribution',
         'perfomance_summary/community_contribution',
         'mproject_performance/bucks_target',
         'mproject_performance/bucks_achievement',
         'mproject_performance/bucks_percentage',
         'mproject_performance/does_proceeds_target',
         'mproject_performance/does_proceeds_achievement',
         'mproject_performance/does_proceeds_percentage',
         'mproject_performance/dg_proceeds_target',
         'mproject_performance/dg_proceeds_achievement',
         'mproject_performance/dg_proceeds_percentage',
         'mproject_performance/kr_target',
         'mproject_performance/kr_achievement',
         'mproject_performance/kr_percentage',
         'impact_information/db_target',
         'impact_information/db_achievement',
         'impact_information/db_percentage',
         'impact_information/mb_target',
         'impact_information/mb_achievement',
         'impact_information/mb_percentage',
         'impact_information/fb_target',
         'impact_information/fb_achievement',
         'impact_information/fb_percentage',
         'impact_information/vb_target',
         'impact_information/vb_achievement',
         'impact_information/vb_percentage',
         'mproject_performance/m_production_target',
         'mproject_performance/m_production_achievement',
         'mproject_performance/m_production_percentage',
         'impact_information/grp_income_target',
         'impact_information/grp_income_achievement',
         'impact_information/grp_income_percentage',
         'impact_information/milk_bnf_sale_target',
         'impact_information/milk_bnf_sale_achievement',
         'impact_information/milk_bnf_sale_percentage'
         )
     ),
    (DAIRY_COWS_PROJECT_REPORT,
        ('perfomance_summary/exp_contribution',
         'perfomance_summary/actual_contribution',
         'perfomance_summary/community_contribution',
         'mproject_performance/cows_target',
         'mproject_performance/cows_achievement',
         'mproject_performance/cows_percentage',
         'mproject_performance/cws_proceeds_target',
         'mproject_performance/cws_proceeds_achievement',
         'mproject_performance/cws_proceeds_percentage',
         'mproject_performance/cr_target',
         'mproject_performance/cr_achievement',
         'mproject_performance/cr_percentage',
         'impact_information/db_target',
         'impact_information/db_achievement',
         'impact_information/db_percentage',
         'impact_information/fb_target',
         'impact_information/fb_achievement',
         'impact_information/fb_percentage',
         'impact_information/mb_target',
         'impact_information/mb_achievement',
         'impact_information/mb_percentage',
         'impact_information/vb_target',
         'impact_information/vb_achievement',
         'impact_information/vb_percentage',
         'mproject_performance/m_acquired_target',
         'mproject_performance/m_acquired_achievement',
         'mproject_performance/m_acquired_percentage',
         'mproject_performance/msold_bnf_target',
         'mproject_performance/msold_bnf_achievement',
         'mproject_performance/msold_bnf_percentage',
         'impact_information/milk_bnf_sale_target',
         'impact_information/milk_bnf_sale_achievement',
         'impact_information/milk_bnf_sale_percentage',
         'mproject_performance/ai_target',
         'mproject_performance/ai_achievement',
         'mproject_performance/ai_percentage',
         'impact_information/milk_grp_sale_target',
         'impact_information/milk_grp_sale_achievement',
         'impact_information/milk_grp_sale_percentage'
         )
     ),
    (FIC_PROJECT_REPORT, ('')),
    (BODABODA_PROJECT_REPORT, ('')),
    (POULTRY_PROJECT_REPORT, (''))
}

IMPACT_INDICATOR_KEYS = (
    ('no_of_b_increased_income', 'impact_information/b_income'),
    ('no_of_b_improved_houses', 'impact_information/b_improved_houses'),
    ('no_of_b_hh_assets', 'impact_information/b_hh_assets'),
    ('no_of_children', 'impact_information/no_children')
)

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
    DAIRY_GOAT_PROJECT_REPORT: (
        ('exp_contribution', 'perfomance_summary/exp_contribution'),
        ('actual_contribution', 'perfomance_summary/actual_contribution'),
        ('community_contribution',
            'perfomance_summary/community_contribution'),
        ('bucks_target', 'mproject_performance/bucks_target'),
        ('bucks_achievement', 'mproject_performance/bucks_achievement'),
        ('bucks_percentage', 'mproject_performance/bucks_percentage'),
        ('does_proceeds_target',
            'mproject_performance/does_proceeds_target'),
        ('does_proceeds_achievement',
            'mproject_performance/does_proceeds_achievement'),
        ('does_proceeds_percentage',
            'mproject_performance/does_proceeds_percentage'),
        ('dg_proceeds_target', 'mproject_performance/dg_proceeds_target'),
        ('dg_proceeds_achievement',
            'mproject_performance/dg_proceeds_achievement'),
        ('dg_proceeds_percentage',
            'mproject_performance/dg_proceeds_percentage'),
        ('kr_target', 'mproject_performance/kr_target'),
        ('kr_achievement', 'mproject_performance/kr_achievement'),
        ('kr_percentage', 'mproject_performance/kr_percentage'),
        ('db_target', 'impact_information/db_target'),
        ('db_achievement', 'impact_information/db_achievement'),
        ('db_percentage', 'impact_information/db_percentage'),
        ('mb_target', 'impact_information/mb_target'),
        ('mb_achievement', 'impact_information/mb_achievement'),
        ('mb_percentage', 'impact_information/mb_percentage'),
        ('fb_target', 'impact_information/fb_target'),
        ('fb_achievement', 'impact_information/fb_achievement'),
        ('fb_percentage', 'impact_information/fb_percentage'),
        ('vb_target', 'impact_information/vb_target'),
        ('vb_achievement', 'impact_information/vb_achievement'),
        ('vb_percentage', 'impact_information/vb_percentage'),
        ('m_production_target', 'mproject_performance/m_production_target'),
        ('m_production_achievement',
            'mproject_performance/m_production_achievement'),
        ('m_production_percentage',
            'mproject_performance/m_production_percentage'),
        ('grp_income_target', 'impact_information/grp_income_target'),
        ('grp_income_achievement',
            'impact_information/grp_income_achievement'),
        ('grp_income_percentage', 'impact_information/grp_income_percentage'),
        ('milk_bnf_sale_target', 'impact_information/milk_bnf_sale_target'),
        ('milk_bnf_sale_achievement',
            'impact_information/milk_bnf_sale_achievement'),
        ('milk_bnf_sale_percentage',
            'impact_information/milk_bnf_sale_percentage')
    ),
    DAIRY_COWS_PROJECT_REPORT: (
        ('exp_contribution', 'perfomance_summary/exp_contribution'),
        ('actual_contribution', 'perfomance_summary/actual_contribution'),
        ('community_contribution',
            'perfomance_summary/community_contribution'),
        ('cows_target', 'mproject_performance/cows_target'),
        ('cows_achievement', 'mproject_performance/cows_achievement'),
        ('cows_percentage', 'mproject_performance/cows_percentage'),
        ('cws_proceeds_target', 'mproject_performance/cws_proceeds_target'),
        ('cws_proceeds_achievement',
            'mproject_performance/cws_proceeds_achievement'),
        ('cws_proceeds_percentage',
            'mproject_performance/cws_proceeds_percentage'),
        ('cr_target', 'mproject_performance/cr_target'),
        ('cr_achievement', 'mproject_performance/cr_achievement'),
        ('cr_percentage', 'mproject_performance/cr_percentage'),
        ('db_target', 'impact_information/db_target'),
        ('db_achievement', 'impact_information/db_achievement'),
        ('db_percentage', 'impact_information/db_percentage'),
        ('fb_target', 'impact_information/fb_target'),
        ('fb_achievement', 'impact_information/fb_achievement'),
        ('fb_percentage', 'impact_information/fb_percentage'),
        ('mb_target', 'impact_information/mb_target'),
        ('mb_achievement', 'impact_information/mb_achievement'),
        ('mb_percentage', 'impact_information/mb_percentage'),
        ('vb_target', 'impact_information/vb_target'),
        ('vb_achievement', 'impact_information/vb_achievement'),
        ('vb_percentage', 'impact_information/vb_percentage'),
        ('m_acquired_target', 'mproject_performance/m_acquired_target'),
        ('m_acquired_achievement',
            'mproject_performance/m_acquired_achievement'),
        ('m_acquired_percentage',
            'mproject_performance/m_acquired_percentage'),
        ('msold_bnf_target', 'mproject_performance/msold_bnf_target'),
        ('msold_bnf_achievement',
            'mproject_performance/msold_bnf_achievement'),
        ('msold_bnf_percentage', 'mproject_performance/msold_bnf_percentage'),
        ('milk_bnf_sale_target', 'impact_information/milk_bnf_sale_target'),
        ('milk_bnf_sale_achievement',
            'impact_information/milk_bnf_sale_achievement'),
        ('milk_bnf_sale_percentage',
            'impact_information/milk_bnf_sale_percentage'),
        ('ai_target', 'mproject_performance/ai_target'),
        ('ai_achievement', 'mproject_performance/ai_achievement'),
        ('ai_percentage', 'mproject_performance/ai_percentage'),
        ('milk_grp_sale_target', 'impact_information/milk_grp_sale_target'),
        ('milk_grp_sale_achievement',
            'impact_information/milk_grp_sale_achievement'),
        ('milk_grp_sale_percentage',
            'impact_information/milk_grp_sale_percentage')
    ),
    FIC_PROJECT_REPORT: (
        ('exp_contribution', 'perfomance_summary/exp_contribution'),
        ('actual_contribution', 'perfomance_summary/actual_contribution'),
        ('community_contribution',
            'perfomance_summary/community_contribution'),
        ('pm_target', 'mproject_performance/pm_target'),
        ('pm_achievement', 'mproject_performance/pm_achievement'),
        ('pm_percentage', 'mproject_performance/pm_percentage'),
        ('pm_proceeds_target', 'mproject_performance/pm_proceeds_target'),
        ('pm_proceeds_achievement',
            'mproject_performance/pm_proceeds_achievement'),
        ('pm_proceeds_percentage',
            'mproject_performance/pm_proceeds_percentage'),
        ('acreage_target', 'mproject_performance/acreage_target'),
        ('acreage_achievement', 'mproject_performance/acreage_achievement'),
        ('acreage_percentage', 'mproject_performance/acreage_percentage'),
        ('acreage_bnf_target', 'mproject_performance/acreage_bnf_target'),
        ('acreage_bnf_target', 'mproject_performance/acreage_bnf_achievement'),
        ('acreage_bnf_percentage',
            'mproject_performance/acreage_bnf_percentage'),
        ('db_target', 'impact_information/db_target'),
        ('db_achievement', 'impact_information/db_achievement'),
        ('db_percentage', 'impact_information/db_percentage'),
        ('fb_target', 'impact_information/fb_target'),
        ('fb_achievement', 'impact_information/fb_achievement'),
        ('fb_percentage', 'impact_information/fb_percentage'),
        ('mb_target', 'impact_information/mb_target'),
        ('mb_achievement', 'impact_information/mb_achievement'),
        ('mb_percentage', 'impact_information/mb_percentage'),
        ('vb_target', 'impact_information/vb_target'),
        ('vb_achievement', 'impact_information/vb_achievement'),
        ('vb_percentage', 'impact_information/vb_percentage'),
        ('crop_yield_target', 'mproject_performance/crop_yield_target'),
        ('crop_yield_achievement',
            'mproject_performance/crop_yield_achievement'),
        ('crop_yield_percentage',
            'mproject_performance/crop_yield_percentage'),
        ('grp_target', 'impact_information/grp_target'),
        ('grp_achievement', 'impact_information/grp_achievement'),
        ('grp_percentage', 'impact_information/grp_percentage'),
        ('bnf_income_target', 'impact_information/bnf_income_target'),
        ('bnf_income_achievement',
            'impact_information/bnf_income_achievement'),
        ('bnf_income_percentage', 'impact_information/bnf_income_percentage')
    ),
    BODABODA_PROJECT_REPORT: (
        ('exp_contribution', 'perfomance_summary/exp_contribution'),
        ('actual_contribution', 'perfomance_summary/actual_contribution'),
        ('db_target', 'impact_information/db_target'),
        ('db_achievement', 'impact_information/db_achievement'),
        ('db_percentage', 'impact_information/db_percentage'),
        ('mb_target', 'impact_information/mb_target'),
        ('mb_achievement', 'impact_information/mb_achievement'),
        ('mb_percentage', 'impact_information/mb_percentage'),
        ('fb_target', 'impact_information/fb_target'),
        ('fb_achievement', 'impact_information/fb_achievement'),
        ('fb_percentage', 'impact_information/fb_percentage'),
        ('vb_target', 'impact_information/vb_target'),
        ('vb_achievement', 'impact_information/vb_achievement'),
        ('vb_percentage', 'impact_information/vb_percentage'),
        ('mbs_target', 'mproject_performance/mbs_target'),
        ('mbs_achievement', 'mproject_performance/mbs_achievement'),
        ('mbs_percentage', 'mproject_performance/mbs_percentage'),
        ('mbs_proceeds_target', 'mproject_performance/mbs_proceeds_target'),
        ('mbs_proceeds_achievement',
            'mproject_performance/mbs_proceeds_achievement'),
        ('mbs_proceeds_percentage',
            'mproject_performance/mbs_proceeds_percentage'),
        ('grp_target', 'mproject_performance/grp_target'),
        ('grp_achievement', 'mproject_performance/grp_achievement'),
        ('grp_percentage', 'mproject_performance/grp_percentage'),
        ('bnf_income_target', 'impact_information/bnf_income_target'),
        ('bnf_income_achievement',
            'impact_information/bnf_income_achievement'),
        ('bnf_income_percentage', 'impact_information/bnf_income_percentage')
    ),
    POULTRY_PROJECT_REPORT: (
        ('exp_contribution', 'perfomance_summary/exp_contribution'),
        ('actual_contribution', 'perfomance_summary/actual_contribution'),
        ('birds_target', 'mproject_performance/birds_target'),
        ('birds_achievement', 'mproject_performance/birds_achievement'),
        ('birds_percentage', 'mproject_performance/birds_percentage'),
        ('birds_proceeds_target',
            'mproject_performance/birds_proceeds_target'),
        ('birds_proceeds_percentage',
            'mproject_performance/birds_proceeds_percentage'),
        ('birds_proceeds_achievement',
            'mproject_performance/birds_proceeds_achievement'),
        ('pu_target', 'mproject_performance/pu_target'),
        ('pu_achievement', 'mproject_performance/pu_achievement'),
        ('pu_percentage', 'mproject_performance/pu_percentage'),
        ('db_target', 'impact_information/db_target'),
        ('db_achievement', 'impact_information/db_achievement'),
        ('db_percentage', 'impact_information/db_percentage'),
        ('mb_target', 'impact_information/mb_target'),
        ('mb_achievement', 'impact_information/mb_achievement'),
        ('mb_percentage', 'impact_information/mb_percentage'),
        ('fb_target', 'impact_information/fb_target'),
        ('fb_achievement', 'impact_information/fb_achievement'),
        ('fb_percentage', 'impact_information/fb_percentage'),
        ('vb_target', 'impact_information/vb_target'),
        ('vb_achievement', 'impact_information/vb_achievement'),
        ('vb_percentage', 'impact_information/vb_percentage'),
        ('cr_target', 'mproject_performance/cr_target'),
        ('cr_percentage', 'mproject_performance/cr_percentage'),
        ('dbirds_number', 'mproject_performance,dbirds_number'),
        ('bsold_target', 'mproject_performance/bsold_target'),
        ('bsold_achievement', 'mproject_performance/bsold_achievement'),
        ('bsold_percentage', 'mproject_performance/bsold_percentage'),
        ('eprd_target', 'mproject_performance/eprd_target'),
        ('eprd_target', 'mproject_performance/eprd_target'),
        ('eprd_achievement', 'mproject_performance/eprd_achievement'),
        ('eprd_percentage', 'mproject_performance/eprd_percentage'),
        ('esold_target', 'mproject_performance/esold_target'),
        ('esold_achievement', 'mproject_performance/esold_achievement'),
        ('esold_percentage', 'mproject_performance/esold_percentage'),
        ('grp_target', 'mproject_performance/grp_target'),
        ('grp_achievement', 'mproject_performance/grp_achievement'),
        ('grp_percentage', 'mproject_performance/grp_percentage'),
        ('bnf_income_target', 'mproject_performance/bnf_income_target'),
        ('bnf_income_achievement',
            'mproject_performance/bnf_income_achievement'),
        ('bnf_income_percentage', 'mproject_performance/bnf_income_percentage')
    )
}

IMPACT_INDICATOR_KEYS = (
    ('no_of_b_increased_income', 'impact_information/b_income'),
    ('no_of_b_improved_houses', 'impact_information/b_improved_houses'),
    ('no_of_b_hh_assets', 'impact_information/b_hh_assets'),
    ('no_of_children', 'impact_information/no_children')
)

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
    (DAIRY_GOAT_PROJECT_REPORT, ('')),
    (DAIRY_COWS_PROJECT_REPORT), ('')),
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

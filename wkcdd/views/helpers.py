import json
import datetime

from pyramid.events import subscriber, NewRequest

from wkcdd import constants
from wkcdd.libs.utils import get_performance_indicator_list
from wkcdd.models import (
    County,
    SubCounty,
    Constituency,
    Community,
    Project,
    Location,
    Report
)

from wkcdd.models.report import ReportHandlerError

from wkcdd.models.helpers import (
    get_community_ids_for,
    get_project_list
)


PROJECT_LEVEL = 'projects'
COUNTIES_LEVEL = 'counties'
SUB_COUNTIES_LEVEL = 'sub_counties'
CONSTITUENCIES_LEVEL = 'constituencies'
COMMUNITIES_LEVEL = 'communities'
PROJECTS_LEVEL = 'projects'
DEFAULT_OPTION = 'default'


@subscriber(NewRequest)
def requested_xlsx_format(event):
    request = event.request
    if request.GET.get('format') == 'xlsx':
        request.override_renderer = 'xlsx'
        return True


def filter_projects_by(criteria):
    project_criteria = []
    community_ids = []
    if "name" in criteria:
        project_criteria.append(
            Project.name.ilike("%" + criteria['name'] + "%"))
    if "sector" in criteria:
        project_criteria.append(
            Project.sector.like("%" + criteria['sector'] + "%"))
    if "location_map" in criteria:
        value = get_lowest_location_value(criteria['location_map'])
        if value:
            location = Location.get(Location.id == value)
            community_ids = get_community_ids_for(type(location),
                                                  [location.id])
    if project_criteria and not community_ids:
        projects = Project.all(*project_criteria)
    else:
        projects = get_project_list(community_ids, *project_criteria)
    return projects


def get_lowest_location_value(location_map):
    if location_map:
        value = (location_map['community'] or
                 location_map['constituency'] or
                 location_map['sub_county'] or
                 location_map['county'])
        return value


def get_project_geolocations(projects):
    """
    Get project geopoints for a list of projects
    """
    project_geopoints = [
        {'id': project.id,
         'name': project.name.title(),
         'sector': project.sector_name,
         'lat': str(project.latlong[0]),
         'lng': str(project.latlong[1])}
        for project in projects if project.latlong]

    return project_geopoints


def get_geolocations_from_items(items, sector_id=None):
    # generate project_geopoints from project list
    geolocations = []
    for item in items:
        # get reports for this location or project,
        if sector_id:
            project_filter_criteria = Project.sector == sector_id
            projects = item.get_projects(project_filter_criteria)
        else:
            projects = item.get_projects()
        geolocations.extend(
            get_project_geolocations(projects))
    return geolocations


def name_to_location_type(level):
    level_to_location_type_map = {
        COUNTIES_LEVEL: County,
        SUB_COUNTIES_LEVEL: SubCounty,
        CONSTITUENCIES_LEVEL: Constituency,
        COMMUNITIES_LEVEL: Community,
        PROJECTS_LEVEL: Project
    }
    return level_to_location_type_map[level]


def get_target_class_from_view_by(view_by, source_class=None):
    """
    Determine the target class based on the active/source class and view_by
    value

    If view_by is None, our target class is the child class of source e.g.
     For County, the child class is SubCounty
    """

    if view_by is None:
        if source_class is None:
            raise ValueError(
                "You must specify source_class if view_by is None")
        return source_class.get_child_class()
    else:
        return name_to_location_type(view_by)


def get_performance_sector_mapping(sector=None):
    """
    Returns sector mapping containing the registration id, report_id
    and label for display purposes
    """
    if sector:
        return (
            [(reg_id, report_id, label)
             for reg_id, report_id, label in constants.PROJECT_TYPE_MAPPING
             if reg_id == sector])
    else:
        return (
            [(reg_id, report_id, label)
             for reg_id, report_id, label in constants.PROJECT_TYPE_MAPPING])


def get_sector_data(sector_id, report_id, child_locations, *period_criteria):
    indicators = get_performance_indicator_list(
        constants.PERFORMANCE_INDICATORS[report_id])
    # child locations should filter project by sector
    project_filter_criteria = Project.sector == sector_id

    kwargs = {'project_filter_criteria': project_filter_criteria,
              'period_criteria': period_criteria}

    rows, summary_row = Report.generate_performance_indicators(
        child_locations, indicators, **kwargs)

    return {
        'rows': rows,
        'summary_row': summary_row
    }


def get_sector_periods(sector_id, child_locations):
    project_filter_criteria = Project.sector == sector_id
    periods = Report.get_periods_for(
        child_locations, project_filter_criteria)
    return periods


def build_report_period_criteria(month_or_quarter, period):
    criteria = []
    if month_or_quarter:
        # months and quarters are related even though they are different values
        try:
            month = int(month_or_quarter)
            criteria.extend([Report.month == month])
        except ValueError:
            quarter = month_or_quarter
            criteria.extend([Report.quarter == quarter])

    if period:
        criteria.extend([Report.period == period])

    return criteria


def build_impact_indicator_chart_dataset(indicators, rows):
    """
    Generate JSON dataset
        {
            labels: ['location a', 'location b', 'location c'],
            series: { 'increased_income': [1,2,3,4],
                      'improved_households': [5,6,7,8]
                    }
        }
    """
    dataset = {}
    indicator_keys = [item['key'] for item in indicators]
    labels = [row['location'].pretty for row in rows]
    series = {}

    for key in indicator_keys:
        indicator_series = []

        for row in rows:
            if row['indicators']:
                indicator_series.append(row['indicators'][key])

        series[key] = indicator_series

    dataset['labels'] = labels
    dataset['series'] = series

    return json.dumps(dataset)


def build_performance_indicator_chart_dataset(indicators, rows):
    """
    Generate JSON dataset
        {
            labels: ['location a', 'location b', 'location c'],
            series: { 'sector label a': [1%,2%,3%,4%],
                      'sector label b': [5%,6%,7%,8%]
                    }
        }
    """
    dataset = {}

    # Exclude labels that have no ratio field
    indicator_keys = [key_group[2]
                      for label, key_group in indicators if key_group[2]]
    labels = [row['location'].pretty for row in rows]
    series = {}

    for key in indicator_keys:
        indicator_series = []

        for row in rows:
            if row['indicators']:
                indicator_series.append(row['indicators'][key])

        series[key] = indicator_series

    dataset['labels'] = labels
    dataset['series'] = series

    return json.dumps(dataset)


def report_submission_handler(payload):
    payload = json.loads(payload)
    try:
        xform_id = payload.get(constants.XFORM_ID)
        project_report_code = [project_report_code
                               for project_report_form, project_report_code
                               in constants.PROJECT_REPORT_FORMS
                               if project_report_form == xform_id][0]
        report_submission = Report(
            project_code=payload.get(project_report_code),
            submission_time=datetime.datetime.strptime(
                payload.get(constants.REPORT_SUBMISSION_TIME),
                "%Y-%m-%dT%H:%M:%S"),
            month=payload.get(constants.REPORT_MONTH),
            quarter=payload.get(constants.REPORT_QUARTER),
            period=payload.get(constants.REPORT_PERIOD),
            report_data=payload
        )
        Report.add_report_submission(report_submission)
    except (KeyError, IndexError):
        raise ReportHandlerError(
            "'{}' not found in json".format(constants.XFORM_ID))

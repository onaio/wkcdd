import json
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

    project_geopoints = json.dumps(project_geopoints)

    return project_geopoints


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

    rows, summary_row, projects = Report.generate_performance_indicators(
        child_locations, indicators, **kwargs)

    # generate project_geopoints from project list
    project_geopoints = get_project_geolocations(projects)
    return {
        'rows': rows,
        'summary_row': summary_row,
        'project_geopoints': project_geopoints
    }


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
            series: [[1,2,3,4], [5,6,7,8], [9,10,11,12]],
            series_labels: ['Increased income', 'Improved households']
        }
    """
    dataset = {}
    series_labels = [item['label'] for item in indicators]
    indicator_keys = [item['key'] for item in indicators]
    labels = [row['location'].pretty for row in rows]
    series = []

    for key in indicator_keys:
        indicator_series = []

        for row in rows:
            if row['indicators']:
                indicator_series.append(row['indicators'][key])

        series.append(indicator_series)

    dataset['labels'] = labels
    dataset['series'] = series
    dataset['series_labels'] = series_labels

    return json.dumps(dataset)

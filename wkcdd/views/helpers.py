import json
from pyramid.events import subscriber, NewRequest

from wkcdd import constants
from wkcdd.libs.utils import humanize, tuple_to_dict_list
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
    get_community_ids,
    get_constituency_ids,
    get_sub_county_ids,
    get_project_list,
    get_project_types
)


@subscriber(NewRequest)
def requested_xlsx_format(event):
    request = event.request
    if request.GET.get('format') == 'xlsx':
        request.override_renderer = 'xlsx'
        return True


def build_dataset(location_type, locations, impact_indicators, projects=None):
    headers = [humanize(location_type).title()]
    indicator_headers, indicator_keys = zip(*constants.IMPACT_INDICATOR_REPORT)
    headers.extend(indicator_headers)
    rows = []
    summary_row = []

    if projects:
        for project_indicator in impact_indicators['indicator_list']:
            for project in projects:
                if project.id == project_indicator['project_id']:
                    row = [project]
            for key in indicator_keys:
                value = 0 if project_indicator['indicators'] is \
                    None else project_indicator['indicators'][key]
                row.extend([value])
            rows.append(row)
        summary_row.extend([impact_indicators['summary']
                            [key] for key in indicator_keys])
    else:
        for location in locations:
            row = [location]
            location_summary = \
                (impact_indicators['aggregated_impact_indicators']
                 [location.id]['summary'])
            row.extend([location_summary[key] for key in indicator_keys])
            rows.append(row)

        summary_row.extend([impact_indicators['total_indicator_summary']
                            [key] for key in indicator_keys])

    return{
        'headers': headers,
        'rows': rows,
        'summary_row': summary_row
    }


def filter_projects_by(criteria):
    project_criteria = []
    community_ids = []
    if "name" in criteria:
        project_criteria.append(
            Project.name.ilike("%"+criteria['name']+"%"))
    if "sector" in criteria:
        project_criteria.append(
            Project.sector.like("%"+criteria['sector']+"%"))
    if "location_map" in criteria:
        value = get_lowest_location_value(criteria['location_map'])
        if value:
            location = Location.get(Location.id == value)
            community_ids = {
                Community: [value],
                Constituency: get_community_ids([value]),
                SubCounty: get_community_ids(get_constituency_ids
                                             ([value])),
                County: get_community_ids(get_constituency_ids
                                          (get_sub_county_ids
                                           ([value])))
            }[type(location)]
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


def generate_impact_indicators_for(location_map, level=None):
    location_id = get_lowest_location_value(location_map)
    location = None
    aggregate_list = []
    aggregate_type = ''

    if location_id:
        location = Location.get(Location.id == location_id)
        level_map = {
            None: location.children(),
            'county': '',
            'sub_county': '',
            'constituency': '',
            'community': ''
        }
        aggregate_list = level_map[level]
    else:
        # Default aggregation level is all counties
        aggregate_list = County.all()

    if aggregate_list:
        impact_indicators = (
            Report.get_impact_indicator_aggregation_for(
                aggregate_list))
        aggregate_type = aggregate_list[0].location_type

    elif location and type(location) is Community:
            aggregate_list = location.projects
            impact_indicators = Report.get_aggregated_impact_indicators(
                aggregate_list)
            aggregate_type = 'Project'

    return {
        'aggregate_type': aggregate_type,
        'location': location,
        'aggregate_list': aggregate_list,
        'impact_indicators': impact_indicators
    }


def generate_performance_indicators_for(location_map,
                                        sector=None,
                                        level=None):
    sector_indicator_mapping = {}
    sector_aggregated_indicators = {}
    location_id = get_lowest_location_value(location_map)

    if location_id:
        location = Location.get(Location.id == location_id)

        level_map = {
            None: location.children(),
            'county': '',
            'sub_county': '',
            'constituency': '',
            'community': ''
        }

        aggregate_list = level_map[level]
    else:
        # Default aggregation level is all counties
        aggregate_list = County.all()

    location_ids = [child_location.id
                    for child_location in aggregate_list]

    project_types_mappings = get_project_types(
        get_community_ids(
            get_constituency_ids(
                location_ids)))

    for reg_id, report_id, title in project_types_mappings:
        # Skip execution until the selected sector is encountered

        if sector and reg_id != sector:
            continue

        aggregated_indicators = (
            Report.get_performance_indicator_aggregation_for(
                aggregate_list, report_id))

        indicator_mapping = tuple_to_dict_list(
            ('title', 'group'),
            constants.PERFORMANCE_INDICATOR_REPORTS[report_id])

        sector_indicator_mapping[reg_id] = indicator_mapping
        sector_aggregated_indicators[reg_id] = aggregated_indicators

    return {
        'project_types': project_types_mappings,
        'sector_aggregated_indicators': sector_aggregated_indicators,
        'sector_indicator_mapping': sector_indicator_mapping
    }


def get_project_geolocations(projects):
    """
    Get project geopoints for a list of projects
    """
    project_geopoints = [
        {'id': project.id,
         'name': project.name,
         'sector': project.sector_name,
         'lat': str(project.latlong[0]),
         'lng': str(project.latlong[1])}
        for project in projects if project.latlong]

    project_geopoints = json.dumps(project_geopoints)

    return project_geopoints

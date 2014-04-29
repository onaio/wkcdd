import json
from pyramid.events import subscriber, NewRequest

from wkcdd import constants
from wkcdd.libs.utils import humanize
from wkcdd.models import (
    County,
    Community,
    Project,
    Location,
    Report
)
from wkcdd.models.helpers import (
    get_community_ids_for,
    get_project_list,
    get_project_types
)

PROJECT_LABEL = 'projects'


@subscriber(NewRequest)
def requested_xlsx_format(event):
    request = event.request
    if request.GET.get('format') == 'xlsx':
        request.override_renderer = 'xlsx'
        return True


def build_dataset(location_type,
                  locations,
                  indicators,
                  projects=None):
    headers = [humanize(location_type).title()]
    indicator_headers, indicator_keys = zip(*constants.IMPACT_INDICATOR_REPORT)
    headers.extend(indicator_headers)
    rows = []
    summary_row = []

    if projects:
        for project_indicator in indicators['indicator_list']:
            for project in projects:
                if project.id == project_indicator['project_id']:
                    row = [project]
            for key in indicator_keys:
                value = 0 if project_indicator['indicators'] is \
                    None else project_indicator['indicators'][key]
                row.extend([value])
            rows.append(row)
        summary_row.extend([indicators['summary']
                            [key] for key in indicator_keys])
    else:
        for location in locations:
            row = [location]
            location_summary = (
                indicators['aggregated_impact_indicators']
                [location.id]['summary'])
            row.extend([location_summary[key] for key in indicator_keys])
            rows.append(row)

        summary_row.extend([indicators['total_indicator_summary']
                            [key] for key in indicator_keys])

    return{
        'headers': headers,
        'rows': rows,
        'summary_row': summary_row
    }


def build_performance_dataset(location_type,
                              locations,
                              indicators,
                              projects=None,
                              sector_report_map=None):
    headers = [humanize(location_type).title()]
    indicator_headers, indicator_keys = zip(*sector_report_map)
    headers.extend(indicator_headers)
    rows = []
    summary_row = []

    if projects:
        location = locations[0]
        project_indicators = (
            indicators['aggregated_performance_indicators'][location.id])

        for project_indicator in project_indicators['indicator_list']:
            for project in projects:
                if project.id == project_indicator['project_id']:
                    row = [project]
                    for group in indicator_keys:
                        item_group = []
                        for key in group:
                            value = 0 if project_indicator['indicators'] is \
                                None else project_indicator['indicators'][key]
                            item_group.append(value)
                        row.append(item_group)
            rows.append(row)
        summary_row.extend(
            [
                [project_indicators['summary'][key[0]],
                 project_indicators['summary'][key[1]],
                 project_indicators['summary'][key[2]]]
                for key in indicator_keys])
    else:
        for location in locations:
            row = [location]
            location_summary = (
                indicators['aggregated_performance_indicators']
                [location.id]['summary'])
            for group in indicator_keys:
                item_group = []
                for item in group:
                    item_group.append(location_summary[item])

                row.append(item_group)

            rows.append(row)

        summary_row.extend(
            [
                [indicators['total_indicator_summary'][key[0]],
                 indicators['total_indicator_summary'][key[1]],
                 indicators['total_indicator_summary'][key[2]]]
                for key in indicator_keys])

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
            aggregate_type = "Project"

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
    project_type_geopoints = {}
    location_id = get_lowest_location_value(location_map)
    location = None
    aggregate_type = None

    if location_id:
        location = Location.get(Location.id == location_id)

        level_map = {
            None: location.children(),
            'county': '',
            'sub_county': '',
            'constituency': '',
            'community': ''
        }

        if isinstance(location, Community):
            aggregate_list = location.projects
            aggregate_type = PROJECT_LABEL
            location_ids = [location.id]
        else:
            aggregate_list = level_map[level]
            aggregate_type = aggregate_list[0].location_type

        # fetch community ids for selected location type
        community_ids = get_community_ids_for(type(location), [location.id])

    else:
        aggregate_list = County.all()
        aggregate_type = aggregate_list[0].location_type
        location_ids = [location.id for location in aggregate_list]
        community_ids = get_community_ids_for(County, location_ids)

    project_types_mappings = get_project_types(community_ids)

    for reg_id, report_id, title in project_types_mappings:
        # Skip execution until the selected sector is encountered
        if sector and reg_id != sector:
            continue
        indicator_mapping = (
            constants.PERFORMANCE_INDICATOR_REPORTS[report_id])
        if aggregate_type == PROJECT_LABEL:
            aggregated_indicators = (
                Report.get_performance_indicator_aggregation_for(
                    [location], report_id))
            project_geopoints = get_project_geolocations(
                aggregated_indicators['project_list'])

            dataset = build_performance_dataset(
                aggregate_type,
                [location],
                aggregated_indicators,
                projects=aggregate_list,
                sector_report_map=indicator_mapping)
        else:
            aggregated_indicators = (
                Report.get_performance_indicator_aggregation_for(
                    aggregate_list, report_id))
            project_geopoints = get_project_geolocations(
                aggregated_indicators['project_list'])

            dataset = build_performance_dataset(
                aggregate_type,
                aggregate_list,
                aggregated_indicators,
                sector_report_map=indicator_mapping)

        project_type_geopoints[reg_id] = project_geopoints
        sector_indicator_mapping[reg_id] = indicator_mapping
        sector_aggregated_indicators[reg_id] = dataset

    return {
        'project_types': project_types_mappings,
        'location': location,
        'aggregate_type': aggregate_type,
        'aggregate_list': aggregate_list,
        'sector_aggregated_indicators': sector_aggregated_indicators,
        'sector_indicator_mapping': sector_indicator_mapping,
        'project_type_geopoints': project_type_geopoints
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

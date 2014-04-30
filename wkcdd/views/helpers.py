import json
from pyramid.events import subscriber, NewRequest

from wkcdd import constants
from wkcdd.libs.utils import humanize
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
    get_project_list,
    get_project_types
)

PROJECT_LABEL = 'projects'
COUNTIES_LABEL = 'counties'
SUB_COUNTIES_LABEL = 'sub_counties'
CONSTITUENCIES_LABEL = 'constituencies'
COMMUNITIES_LABEL = 'communities'


@subscriber(NewRequest)
def requested_xlsx_format(event):
    request = event.request
    if request.GET.get('format') == 'xlsx':
        request.override_renderer = 'xlsx'
        return True


def build_dataset(location_type, locations, impact_indicators, projects=None):

    headers = {
        'county': [humanize(location_type).title()],
        'sub_county': ["County", humanize(location_type).title()],
        'constituency': ["County", "Sub-County",
                         humanize(location_type).title()],
        'community': ["County", "Sub-County", "Constituency",
                      humanize(location_type).title()],
        'Project': ["Country",
                    "Sub-County",
                    "Constituency",
                    "Community",
                    location_type]
    }[location_type]
    indicator_headers, indicator_keys = zip(*constants.IMPACT_INDICATOR_REPORT)
    headers.extend(indicator_headers)
    rows = []
    summary_row = []

    if projects:
        for project_indicator in impact_indicators['indicator_list']:
            for project in projects:
                if project.id == project_indicator['project_id']:
                    row = [project.community.constituency.sub_county.county,
                           project.community.constituency.sub_county,
                           project.community.constituency,
                           project.community,
                           project]
            for key in indicator_keys:
                value = 0 if project_indicator['indicators'] is \
                    None else project_indicator['indicators'][key]
                row.extend([value])
            rows.append(row)
        summary_row.extend([impact_indicators['summary']
                            [key] for key in indicator_keys])
    else:
        for location in locations:
            if location_type == 'county':
                row = [location]
            elif location_type == 'sub_county':
                row = [location.parent, location]
            elif location_type == 'constituency':
                row = [Location.get(
                    Location.id == location.parent.id).parent,
                    location.parent, location]
            elif location_type == 'community':
                row = [Location.get(Location.id ==
                                    Location.get(Location.id ==
                                                 location.parent.id)
                                    .parent.id).parent,
                       Location.get(Location.id == location.parent.id).parent,
                       location.parent,
                       location]

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


def get_aggregate_list_for_location_by_level(location, level):
    level_map_county = {
        None: location.children(),
        COUNTIES_LABEL: '',
        SUB_COUNTIES_LABEL: location.children(),
        CONSTITUENCIES_LABEL: [constituencies
                               for sub_counties in location.children()
                               for constituencies in sub_counties.children()],
        COMMUNITIES_LABEL: [communities
                            for sub_counties in location.children()
                            for constituencies in sub_counties.children()
                            for communities in constituencies.children()],
        'projects': Report.get_projects_from_location(location)
    }
    level_map_sub_county = {
        None: location.children(),
        COUNTIES_LABEL: '',
        SUB_COUNTIES_LABEL: '',
        CONSTITUENCIES_LABEL: [constituencies
                               for constituencies in location.children()],
        COMMUNITIES_LABEL: [communities
                            for constituencies in location.children()
                            for communities in constituencies.children()],
        'projects': Report.get_projects_from_location(location)
    }
    level_map_constituency = {
        None: location.children(),
        COUNTIES_LABEL: '',
        SUB_COUNTIES_LABEL: '',
        CONSTITUENCIES_LABEL: '',
        COMMUNITIES_LABEL: [communities
                            for communities in location.children()],
        'projects': Report.get_projects_from_location(location)
    }

    level_map_community = {
        None: Report.get_projects_from_location(location),
        COUNTIES_LABEL: '',
        SUB_COUNTIES_LABEL: '',
        CONSTITUENCIES_LABEL: '',
        COMMUNITIES_LABEL: '',
        'projects': Report.get_projects_from_location(location)
    }

    aggregate_list = {
        County: level_map_county[level],
        SubCounty: level_map_sub_county[level],
        Constituency: level_map_constituency[level],
        Community: level_map_community[level],
    }[type(location)]

    return aggregate_list


def generate_impact_indicators_for(location_map, level=None):
    location_id = get_lowest_location_value(location_map)
    location = None
    aggregate_list = []
    aggregate_type = ''

    if location_id:
        location = Location.get(Location.id == location_id)
        aggregate_list = \
            get_aggregate_list_for_location_by_level(location, level)

    else:
        # Default aggregation level is all counties
        level_map = {
            None: County.all(),
            COUNTIES_LABEL: County.all(),
            SUB_COUNTIES_LABEL: SubCounty.all(),
            CONSTITUENCIES_LABEL: Constituency.all(),
            COMMUNITIES_LABEL: Community.all(),
            'projects': Project.all()
        }
        aggregate_list = level_map[level]

    if type(aggregate_list[0]) == Project:
        impact_indicators = \
            Report.get_aggregated_impact_indicators(aggregate_list)
        aggregate_type = 'Project'
    else:
        impact_indicators = (
            Report.get_impact_indicator_aggregation_for(
                aggregate_list))
        aggregate_type = aggregate_list[0].location_type

    return {
        'aggregate_type': aggregate_type,
        'location': location,
        'aggregate_list': aggregate_list,
        'impact_indicators': impact_indicators
    }


def generate_performance_indicators_for(location_map,
                                        sector=None,
                                        level=None):
    level_to_location = {
        COUNTIES_LABEL: County,
        SUB_COUNTIES_LABEL: SubCounty,
        CONSTITUENCIES_LABEL: Constituency,
        COMMUNITIES_LABEL: Community
    }
    sector_indicator_mapping = {}
    sector_aggregated_indicators = {}
    project_type_geopoints = {}
    location_id = get_lowest_location_value(location_map)
    location = None
    aggregate_type = None

    if location_id:
        location = Location.get(Location.id == location_id)

        aggregate_list = \
            get_aggregate_list_for_location_by_level(location, level)
        aggregate_type = (
            PROJECT_LABEL
            if isinstance(aggregate_list[0], Project)
            else aggregate_list[0].location_type)

        # fetch community ids for selected location type
        community_ids = get_community_ids_for(type(location), [location.id])

    else:
        level_map = {
            None: County.all(),
            COUNTIES_LABEL: County.all(),
            SUB_COUNTIES_LABEL: SubCounty.all(),
            CONSTITUENCIES_LABEL: Constituency.all(),
            COMMUNITIES_LABEL: Community.all(),
            'projects': Project.all()
        }
        aggregate_list = level_map[level]
        aggregate_type = aggregate_list[0].location_type
        location_ids = [location.id for location in aggregate_list]
        community_ids = get_community_ids_for(
            level_to_location[level],
            location_ids)

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

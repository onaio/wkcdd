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
    Location
)
from wkcdd.models.helpers import (
    get_community_ids,
    get_constituency_ids,
    get_sub_county_ids,
    get_project_list
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
    if "location" in criteria:
        value = (criteria['location']['community'] or
                 criteria['location']['constituency'] or
                 criteria['location']['sub_county'] or
                 criteria['location']['county'])
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

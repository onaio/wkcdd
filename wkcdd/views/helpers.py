import json
import datetime
import urlparse

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
    MONTH_PERIOD,
    QUARTER_PERIOD,
    get_community_ids_for,
    get_project_list,
    get_children_by_level,
    get_period_row
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
    if projects:
        image_url_base = urlparse.urljoin(
            'https://ona.io',
            "attachment/small?media_file={}/attachments/".format(
                "wkcdd"))

        project_geopoints = [
            {'id': project.id,
             'name': project.name.title(),
             'sector': project.sector_name,
             'image_link': (image_url_base + project.image_file),
             'description': project.description,
             'lat': str(project.latlong[0]),
             'lng': str(project.latlong[1])}
            for project in projects if project.latlong]

        return project_geopoints
    else:
        raise ValueError("No projects provided")


def get_geolocations_from_items(items, sector_id=None):
    # generate project_geopoints from project list
    geolocations = []
    for item in items:
        # get reports for this location or project,
        try:
            project_filter_criteria = ''
            if sector_id:
                project_filter_criteria = Project.sector == sector_id

            projects = item.get_projects(project_filter_criteria)
            geolocations.extend(
                get_project_geolocations(projects))
        except ValueError:
            pass
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


def generate_time_series(start_period,
                         end_period,
                         time_class,
                         start_year,
                         end_year):
    """Given time a and b, get all other intervals in between"""

    if time_class == QUARTER_PERIOD:
        time_series = Report.get_quarter_interval(
            start_period, end_period, start_year, end_year)
    elif time_class == MONTH_PERIOD:
        time_series = (
            Report.get_month_interval(
                start_period, end_period, start_year, end_year))
    else:
        time_series = Report.get_year_interval(start_year, end_year)

    return time_series


def get_impact_indicator_trend_report(time_series,
                                      time_class,
                                      indicators,
                                      collection):
    """

    Generate time series data for impact indicators for a given set of
    locations or projects.

    Return ([1,2,3]), # months
           ([
                [10,20,30,40,50], # month 1 data for each location
                [12,13,14,15,16], # month 2 data ''
                [23,24,25,26,27]  # month 3 data ''
           ])# series data
           (['Siaya', 'Vihiga', 'Bungoma', 'Kakamega', 'Busia']) # series
    """
    # get reports within the specified period
    # for each period, get values for specified indicator
    # return timeseries, series_data, collection labels
    series_labels = [c.pretty for c in collection]
    series_data_map = {}
    for indicator in indicators:
        indicator_key = indicator['key']
        series_data = []

        for item in collection:
            period_row = get_period_row(
                time_series, time_class, item, indicator_key)

            series_data.append(period_row)

        series_data_map[indicator_key] = series_data

    return series_data_map, series_labels


def get_child_locations(view_by,
                        county,
                        sub_county,
                        constituency,
                        community):
    source_class = County
    target_class = None
    location = None

    location_id = community or constituency or sub_county or county

    if location_id:
        location = Location.get(Location.id == location_id)
        source_class = location.__class__
        location_ids = [location.id]

        target_class = get_target_class_from_view_by(
            view_by, source_class)

        child_ids = get_children_by_level(
            location_ids, source_class, target_class)

        child_locations = target_class.all(target_class.id.in_(child_ids))
    else:
        if view_by is None or view_by == 'counties':
            child_locations = County.all()
        else:
            location_ids = [c.id for c in County.all()]
            target_class = get_target_class_from_view_by(
                view_by, source_class)
            child_ids = get_children_by_level(
                location_ids, source_class, target_class)

            child_locations = target_class.all(
                target_class.id.in_(child_ids))

    return location, child_locations


def process_trend_parameters(periods,
                             start_period,
                             end_period,
                             start_year,
                             end_year):
    months = list(periods['months'])
    months.sort()
    months = [str(m) for m in months]

    quarters = list(periods['quarters'])
    quarters.sort()

    years = list(periods['years'])
    years.sort()

    if months and quarters and years:
        # Retrieve get parameters and provide defaults if none was selected
        start_period = (
            start_period
            if start_period and start_period in (months + quarters)
            else months[0])

        end_period = (
            end_period if end_period and end_period in (months + quarters)
            else months[-1])

        start_year = (
            start_year if start_year and start_year in years else years[-1])

        end_year = (
            end_year if end_year and end_year in years else years[-1])
        return start_period, end_period, start_year, end_year
    else:
        return start_period, end_period, start_year, end_year


def get_performance_indicator_trend_report(sector_id,
                                           time_series,
                                           time_class,
                                           indicators,
                                           collection):
    # Similar to function for generating the impact indicators trend reports
    series_labels = [c.pretty for c in collection]
    series_data_map = {}
    project_filter_criteria = Project.sector == sector_id

    for indicator in indicators:
        indicator_key = indicator['key']
        indicator_property = indicator['property']
        indicator_type = indicator['type']

        if indicator_type == 'ratio':
            series_data = []

            for item in collection:
             # Generate kwargs arguments
                kwargs = {
                    'project_filter_criteria': project_filter_criteria,
                    'indicator_type': indicator_type}

                period_row = get_period_row(
                    time_series, time_class, item, indicator_key, **kwargs)
                
                series_data.append(period_row)

            series_data_map[indicator_property] = series_data

    return series_data_map, series_labels

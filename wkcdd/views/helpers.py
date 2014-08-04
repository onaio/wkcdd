import json
import datetime
import urlparse
import re
from collections import defaultdict

from pyramid.events import subscriber, NewRequest
from pyramid.httpexceptions import HTTPBadRequest

from wkcdd import constants
from wkcdd.libs.utils import (
    number_to_month_name,
    get_performance_indicator_list)
from wkcdd.models import (
    County,
    SubCounty,
    Constituency,
    Community,
    Project,
    Location,
    Report
)

from wkcdd.models.indicator import (
    PercentageIncomeIncreasedIndicator,
    TotalBeneficiariesIndicator,
    TotalFemaleBeneficiariesIndicator,
    CGAAttendanceRatioIndicator,
    CDDCAttendanceRatioIndicator,
    CDDCManagementCountIndicator,
    CIGMemberRatioIndicator,
    SaicComplaintsResolveRatioIndicator,
    SaicMeetingRatioIndicator,
    PMCAttendanceRatioIndicator,
    CIGAttendanceRatioIndicator,
    UpdatedProjectRatioIndicator)

from wkcdd.models.report import ReportHandlerError

from wkcdd.models.helpers import get_children_by_level


PROJECT_LEVEL = 'projects'
COUNTIES_LEVEL = 'counties'
SUB_COUNTIES_LEVEL = 'sub_counties'
CONSTITUENCIES_LEVEL = 'constituencies'
COMMUNITIES_LEVEL = 'communities'
PROJECTS_LEVEL = 'projects'
DEFAULT_OPTION = 'default'

YEAR_PERIOD = 'period'
MONTH_PERIOD = 'month'
QUARTER_PERIOD = 'quarter'


@subscriber(NewRequest)
def requested_xlsx_format(event):
    request = event.request
    if request.GET.get('format') == 'xlsx':
        request.override_renderer = 'xlsx'
        return True


def check_post_csrf(func):
    """
    Verify the csrf_token only if the request method is POST

    Useful when you gave the same view function handling both POST and GET
    requests
    :param func: the decorated view function
    :return: the new callable that decorates the view
    """
    def inner(context, request):
        if request.method == "POST":
            if request.session.get_csrf_token()\
                    != request.POST.get('csrf_token'):
                return HTTPBadRequest("Bad csrf token")
        # fall through if not POST or token is valid
        return func.__call__(context, request)
    return inner


def filter_projects_by(criteria):
    project_criteria = []
    location = criteria['location']
    if "name" in criteria:
        project_criteria.append(
            Project.name.ilike("%" + criteria['name'] + "%"))
    if "sector" in criteria:
        project_criteria.append(
            Project.sector.like("%" + criteria['sector'] + "%"))

    if project_criteria and not location:
        projects = Project.all(*project_criteria)
    else:
        projects = location.get_projects(*project_criteria)
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
    """
    # get reports within the specified period
    # for each period, get values for specified indicator
    # return timeseries, series_data, collection labels
    series_labels = [c.pretty for c in collection]
    series_data_list = []

    for period, year in time_series:
        period_label, time_criteria = get_time_criteria(
            period, year, time_class)

        series_data_list.append(
            Report.get_trend_values_for_impact_indicators(
                collection, indicators, period_label, *time_criteria))

    # map returned data to the chart format
    series_data_map = restructure_impact_trend_data(
        indicators, series_data_list, collection)

    return series_data_map, series_labels


def restructure_impact_trend_data(indicators,
                                  series_data_list,
                                  collection):
    series_data_map = defaultdict(list)

    # iterate through each period data
    for series_data in series_data_list:
        # retrieve indicator values by location

        for indicator in indicators:
            indicator_key = indicator['key']

            for index, item in enumerate(collection):
                trend_value = series_data[item.pretty][indicator_key]
                try:
                    series_data_map[indicator_key][index].extend(
                        [trend_value])
                except IndexError:
                    series_data_map[indicator_key].append(
                        [trend_value])

    return series_data_map


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


def get_default_period(periods,
                       month_or_quarter,
                       year,
                       location_selected=False):
    if periods['months'] and periods['years']:
        years = list(periods['years'])
        years.sort()

        months = list(periods['months'])
        months.sort()
        months = [str(m) for m in months]

        quarters = list(periods['quarters'])
        quarters.sort()

        year = year if year and year in years else years[-1]
        # default month is the latest month
        if location_selected:
            month = (
                month_or_quarter
                if month_or_quarter and month_or_quarter in (months + quarters)
                else months[-1])
        else:
            month = (
                month_or_quarter
                if month_or_quarter and month_or_quarter in (months + quarters)
                else str(Report.get_latest_month_for_year(year)[0]))

        return month, year
    else:
        # values that cannot return any data
        return 0, 0


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

    # validate that periods are of the same type
    if start_period and end_period:
        # test if both are quarters
        valid = False
        valid = (
            True if 'q_' in start_period and 'q_' in end_period else False)
        if not valid:
            try:
                valid = int(start_period) and int(end_period)
            except ValueError:
                raise HTTPBadRequest('Select Months or Quarters but not both')

    # Retrieve get parameters and provide defaults if none was selected
    if months and quarters and years:
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


def get_time_criteria(period, year, time_class):
    period_label = None
    year_label = re.search('\d+', year).group(0)

    if time_class == YEAR_PERIOD:
        time_criteria = Report.period == period
        period_label = year_label

    elif time_class == MONTH_PERIOD:
        time_criteria = [Report.month == period,
                         Report.period == year]
        period_label = (
            number_to_month_name(period) +
            " {}".format(year_label))
    elif time_class == QUARTER_PERIOD:
        time_criteria = [Report.quarter == period,
                         Report.period == year]
        period_label = (period.replace("q_", "Quarter ") +
                        " {}".format(year_label))

    return period_label, time_criteria


def get_performance_indicator_trend_report(sector_id,
                                           time_series,
                                           time_class,
                                           indicators,
                                           collection):
    # Similar to function for generating the impact indicators trend reports
    series_labels = [c.pretty for c in collection]
    series_data_list = []
    project_filter_criteria = Project.sector == sector_id

    for period, year in time_series:
        period_label, time_criteria = get_time_criteria(
            period, year, time_class)
        criteria_args = {
            'project_filter_criteria': project_filter_criteria,
            'time_criteria': time_criteria}

        # each entry in the list is a period entry
        series_data_list.append(
            Report.get_trend_values_for_performance_indicators(
                collection, indicators, period_label, **criteria_args))

    # map data to chart format
    series_data_map = restructure_performance_trend_data(
        indicators, series_data_list, collection)

    return series_data_map, series_labels


def restructure_performance_trend_data(indicators,
                                       series_data_list,
                                       collection):
    series_data_map = defaultdict(list)

    # iterate through each period data
    for series_data in series_data_list:
        # retrieve indicator values by location

        for indicator in indicators:
            indicator_type = indicator['type']

            if indicator_type == 'ratio':
                indicator_property = indicator['property']

                for index, item in enumerate(collection):
                    trend_value = series_data[item.pretty][indicator_property]
                    try:
                        series_data_map[indicator_property][index].extend(
                            [trend_value])
                    except IndexError:
                        series_data_map[indicator_property].append(
                            [trend_value])

    return series_data_map


def get_all_sector_periods(sectors, child_locations, periods):
    for reg_id, report_id, title in sectors:
        sector_periods = get_sector_periods(reg_id, child_locations)

        periods['years'].update(sector_periods['years'])
        periods['months'].update(sector_periods['months'])
        periods['quarters'].update(sector_periods['quarters'])

    return periods


def get_result_framework_indicators(child_locations, period):
    project_ids = []

    for item in child_locations:
        project_ids.extend(item.get_project_ids())

    # percentage increase in income
    income_increase_ratio = PercentageIncomeIncreasedIndicator.get_value(
        project_ids,
        period)

    # total number of beneficiaries
    total_beneficiaries = TotalBeneficiariesIndicator.get_value(
        project_ids,
        period)

    # proportion of female beneficiaries
    total_female_beneficiaries = \
        TotalFemaleBeneficiariesIndicator.get_value(
            project_ids,
            period)

    # percentage of community members participating in CGM
    cga_attendance_ratio = CGAAttendanceRatioIndicator.get_value(period)

    # percentage of PMC members participating in decision making
    pmc_attendance_ratio = PMCAttendanceRatioIndicator.get_value(
        project_ids, period)

    # percentage of CDDC members participating in decision making
    cddc_attendance_ratio = CDDCAttendanceRatioIndicator.get_value(period)

    # percentage of CIG members participating in decisions making
    cig_attendance_ratio = CIGAttendanceRatioIndicator.get_value(
        project_ids, period)

    # No. of CDDC managing development priorities
    cddc_management_count = CDDCManagementCountIndicator.get_value(period)

    # proportion of vulnerable community members
    vulnerable_member_ratio = CIGMemberRatioIndicator.get_value(
        project_ids, period)

    # proportion of complaints resolved
    saic_complaints_resolved_ratio = \
        SaicComplaintsResolveRatioIndicator.get_value(period)

    # proportion of meetings conducted by social audit committees at the
    # community level
    saic_meeting_ratio = SaicMeetingRatioIndicator.get_value(period)

    # percentage of sub-projects including financial information
    updated_sub_projects_ratio = \
        UpdatedProjectRatioIndicator.get_value(project_ids, period)

    to_ratio = lambda x: x * 100

    indicators = {
        'income_increase_ratio': to_ratio(income_increase_ratio),
        'total_beneficiaries': total_beneficiaries,
        'total_female_beneficiaries': total_female_beneficiaries,
        'cga_attendance_ratio': to_ratio(cga_attendance_ratio),
        'pmc_attendance_ratio': to_ratio(pmc_attendance_ratio),
        'cddc_attendance_ratio': to_ratio(cddc_attendance_ratio),
        'cig_attendance_ratio': to_ratio(cig_attendance_ratio),
        'cddc_management_count': cddc_management_count,
        'vulnerable_member_ratio': to_ratio(vulnerable_member_ratio),
        'saic_complaints_resolved_ratio': to_ratio(
            saic_complaints_resolved_ratio),
        'saic_meeting_ratio': to_ratio(saic_meeting_ratio),
        'updated_sub_projects_ratio': to_ratio(updated_sub_projects_ratio)
    }

    return indicators

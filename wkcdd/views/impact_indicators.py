import json
from pyramid.view import (
    view_defaults,
    view_config
)

from wkcdd import constants
from wkcdd.models.helpers import get_children_by_level
from wkcdd.libs.utils import get_impact_indicator_list
from wkcdd.views.helpers import (
    MONTH_PERIOD,
    get_target_class_from_view_by,
    build_report_period_criteria,
    build_impact_indicator_chart_dataset,
    get_geolocations_from_items,
    generate_time_series,
    process_trend_parameters,
    get_child_locations,
    get_impact_indicator_trend_report)
from wkcdd.models.location import LocationFactory
from wkcdd.models import (
    Report,
    County,
    Project,
    Location)


@view_defaults(route_name='impact_indicators')
class ImpactIndicators(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=LocationFactory,
                 renderer='impact_indicators.jinja2',
                 request_method='GET')
    def index(self):
        view_by = self.request.GET.get('view_by') or None
        month_or_quarter = self.request.GET.get('month_or_quarter', '')
        period = self.request.GET.get('period', '')

        source_class = County
        target_class = None

        if view_by is None or view_by == 'counties':
            child_locations = County.all()
        else:
            location_ids = [c.id for c in County.all()]
            target_class = get_target_class_from_view_by(
                view_by, source_class)
            child_ids = get_children_by_level(
                location_ids, source_class, target_class)

            child_locations = target_class.all(target_class.id.in_(child_ids))

        # create a dict mapping to "name, key and label"
        indicators = get_impact_indicator_list(
            constants.IMPACT_INDICATOR_KEYS)

        # generate report period criteria
        criteria = build_report_period_criteria(month_or_quarter, period)

        rows, summary_row = Report.generate_impact_indicators(
            child_locations, indicators, *criteria)

        geo_locations = json.dumps(
            get_geolocations_from_items(child_locations))

        periods = Report.get_periods_for(child_locations)

        chart_dataset = build_impact_indicator_chart_dataset(indicators, rows)
        search_criteria = {'view_by': view_by,
                           'month_or_quarter': month_or_quarter,
                           'period': period,
                           'location': ''}
        filter_criteria = Project.generate_filter_criteria()
        filter_criteria.update(periods)

        return {
            'indicators': indicators,
            'rows': rows,
            'summary_row': summary_row,
            'target_class': target_class,
            'search_criteria': search_criteria,
            'filter_criteria': filter_criteria,
            'chart_dataset': chart_dataset,
            'is_impact': True,
            'geo_locations': geo_locations
        }

    @view_config(name='',
                 context=Location,
                 renderer='impact_indicators.jinja2',
                 request_method='GET')
    def show(self):
        view_by = self.request.GET.get('view_by') or None
        month_or_quarter = self.request.GET.get('month_or_quarter', '')
        period = self.request.GET.get('period', '')

        location = self.request.context
        source_class = location.__class__
        location_ids = [location.id]

        target_class = get_target_class_from_view_by(
            view_by, source_class)

        child_ids = get_children_by_level(
            location_ids, source_class, target_class)

        child_locations = target_class.all(target_class.id.in_(child_ids))
        # create a dict mapping to "name, key and label"
        indicators = get_impact_indicator_list(
            constants.IMPACT_INDICATOR_KEYS)

        # generate report period criteria
        criteria = build_report_period_criteria(month_or_quarter, period)

        rows, summary_row = Report.generate_impact_indicators(
            child_locations, indicators, *criteria)

        geo_locations = json.dumps(
            get_geolocations_from_items(child_locations))

        periods = Report.get_periods_for(child_locations)

        chart_dataset = build_impact_indicator_chart_dataset(indicators, rows)
        search_criteria = {'view_by': view_by,
                           'month_or_quarter': month_or_quarter,
                           'period': period,
                           'location': location}
        filter_criteria = Project.generate_filter_criteria()
        filter_criteria.update(periods)

        return {
            'location': location,
            'indicators': indicators,
            'rows': rows,
            'summary_row': summary_row,
            'target_class': target_class,
            'search_criteria': search_criteria,
            'filter_criteria': filter_criteria,
            'chart_dataset': chart_dataset,
            'is_impact': True,
            'geo_locations': geo_locations
        }

    @view_config(name='trends',
                 context=LocationFactory,
                 renderer='impact_indicators_trends.jinja2',
                 request_method='GET')
    def trends(self):
        # Get list of locations

        view_by = self.request.GET.get('view_by') or None
        county = self.request.GET.get('county') or None
        sub_county = self.request.GET.get('sub_county') or None
        constituency = self.request.GET.get('constituency') or None
        community = self.request.GET.get('community') or None

        location, child_locations = get_child_locations(view_by,
                                                        county,
                                                        sub_county,
                                                        constituency,
                                                        community)

        # Get periods based on the child locations

        periods = Report.get_periods_for(child_locations)
        start_period, end_period, start_year, end_year = (
            process_trend_parameters(periods,
                                     self.request.GET.get('start_period'),
                                     self.request.GET.get('end_period'),
                                     self.request.GET.get('start_year'),
                                     self.request.GET.get('end_year')))

        # handle months or quarters
        time_class = self.request.GET.get('time_class', MONTH_PERIOD)

        # Generate time series range for the map x_axis

        time_series = generate_time_series(
            start_period, end_period, time_class, start_year, end_year)

        indicators = get_impact_indicator_list(
            constants.IMPACT_INDICATOR_KEYS)

        # Generate trend report for all indicators

        series_data_map, series_labels = (
            get_impact_indicator_trend_report(
                time_series,
                time_class,
                indicators,
                child_locations))

        chart_dataset = json.dumps(
            {'labels': time_series,
             'series': series_data_map,
             'seriesLabels': series_labels})

        # update start period based on the retrieved data
        start_period = str(time_series[0][0]) if time_series else ''
        end_period = str(time_series[-1][0]) if time_series else ''

        search_criteria = {'view_by': view_by,
                           'start_period': start_period,
                           'end_period': end_period,
                           'time_class': time_class,
                           'start_year': start_year,
                           'end_year': end_year,
                           'location': location or ''}

        filter_criteria = Project.generate_filter_criteria()

        filter_criteria.update(periods)

        return {
            'chart_dataset': chart_dataset,
            'indicators': indicators,
            'search_criteria': search_criteria,
            'filter_criteria': filter_criteria,
            'time_series': time_series
        }

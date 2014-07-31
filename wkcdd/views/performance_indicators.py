import json
from collections import defaultdict
from pyramid.view import (
    view_defaults,
    view_config
)

from wkcdd import constants
from wkcdd.models.location import LocationFactory
from wkcdd.models.helpers import get_children_by_level
from wkcdd.libs.utils import get_performance_indicator_list
from wkcdd.views.helpers import (
    MONTH_PERIOD,
    get_sector_data,
    get_geolocations_from_items,
    get_performance_sector_mapping,
    get_target_class_from_view_by,
    build_report_period_criteria,
    get_sector_periods,
    get_default_period,
    get_all_sector_periods,
    build_performance_indicator_chart_dataset,
    generate_time_series,
    process_trend_parameters,
    get_child_locations,
    get_performance_indicator_trend_report)
from wkcdd.models import (
    County,
    Project,
    Location)


@view_defaults(route_name='performance_indicators')
class PerformanceIndicators(object):
    PERFORMANCE_INDICATOR_EXPORT_KEY = "performance_export"

    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=LocationFactory,
                 renderer='performance_indicators.jinja2',
                 request_method='GET')
    def index(self):
        view_by = self.request.GET.get('view_by') or None
        sector = self.request.GET.get('sector') or None
        month_or_quarter = self.request.GET.get('month_or_quarter', '')
        period = self.request.GET.get('period', '')

        source_class = County
        target_class = None
        sectors = get_performance_sector_mapping()
        # contains sector: {rows: rows, summary_row: summary_row}
        sector_data = {}
        sector_indicators = {}
        selected_sector = {}
        geo_locations = None
        chart_dataset = None
        periods = defaultdict(set)

        if view_by is None or view_by == 'counties':
            child_locations = County.all()

            # sort locations or projects by name
            child_locations.sort(key=lambda c: c.pretty)
        else:
            location_ids = [c.id for c in County.all()]
            target_class = get_target_class_from_view_by(
                view_by, source_class)
            child_ids = get_children_by_level(
                location_ids, source_class, target_class)

            child_locations = target_class.all(target_class.id.in_(child_ids))

            # sort locations or projects by name
            child_locations.sort(key=lambda c: c.pretty)

        # create a dict mapping to "property, key and type" based on
        # a selected sector or the first sector on the list

        if sector:
            # retrieve sector periods
            periods = get_sector_periods(sector, child_locations)

            # set default period values when none is provided
            month_or_quarter, period = get_default_period(
                periods, month_or_quarter, period)

            # generate report period criteria
            criteria = build_report_period_criteria(month_or_quarter, period)

            reg_id, report_id, label = get_performance_sector_mapping(
                sector)[0]
            sector_data[sector] = get_sector_data(reg_id,
                                                  report_id,
                                                  child_locations,
                                                  *criteria)
            sector_indicators[reg_id] = (
                constants.PERFORMANCE_INDICATOR_REPORTS[report_id])
            selected_sector['sector'] = reg_id
            selected_sector['report'] = report_id
            selected_sector['label'] = label

            # retrieve project sector project geolocations
            geo_locations = json.dumps(
                get_geolocations_from_items(child_locations, reg_id))

            # generate chart_dataset
            chart_dataset = (
                build_performance_indicator_chart_dataset(
                    sector_indicators[reg_id], sector_data[sector]['rows']))

        else:
            periods = get_all_sector_periods(
                sectors, child_locations, periods)

            # set default period values when none is provided
            month_or_quarter, period = get_default_period(
                periods, month_or_quarter, period)

            criteria = build_report_period_criteria(
                month_or_quarter, period)

            for reg_id, report_id, title in sectors:

                sector_data[reg_id] = get_sector_data(reg_id,
                                                      report_id,
                                                      child_locations,
                                                      *criteria)
                sector_indicators[reg_id] = (
                    constants.PERFORMANCE_INDICATOR_REPORTS[report_id])

        search_criteria = {'view_by': view_by,
                           'selected_sector': selected_sector,
                           'month_or_quarter': month_or_quarter,
                           'period': period,
                           'location': ''}
        filter_criteria = Project.generate_filter_criteria()

        filter_criteria.update(periods)

        # return sectors, sector indicator list, sector indicator data.
        return {
            'sectors': sectors,
            'sector_indicators': sector_indicators,
            'sector_data': sector_data,
            'target_class': target_class,
            'search_criteria': search_criteria,
            'filter_criteria': filter_criteria,
            'chart_dataset': chart_dataset,
            'geo_locations': geo_locations,
            self.PERFORMANCE_INDICATOR_EXPORT_KEY: True
        }

    @view_config(name='',
                 context=Location,
                 renderer='performance_indicators.jinja2',
                 request_method='GET')
    def show(self):
        view_by = self.request.GET.get('view_by') or None
        sector = self.request.GET.get('sector') or None
        month_or_quarter = self.request.GET.get('month_or_quarter', '')
        period = self.request.GET.get('period', '')

        location = self.request.context
        source_class = location.__class__
        location_ids = [location.id]
        sectors = get_performance_sector_mapping()
        # contains sector: {rows: rows, summary_row: summary_row}
        sector_data = {}
        sector_indicators = {}
        selected_sector = {}
        chart_dataset = None
        geo_locations = None
        periods = defaultdict(set)

        target_class = get_target_class_from_view_by(view_by, source_class)

        child_ids = get_children_by_level(
            location_ids, source_class, target_class)

        child_locations = target_class.all(target_class.id.in_(child_ids))

        # sort locations or projects by name
        child_locations.sort(key=lambda c: c.pretty)

        # create a dict mapping to "property, key and type" based on
        # a selected sector or the first sector on the list
        if sector:
            # if the specified sector is not in location sector types
            reg_id, report_id, label = get_performance_sector_mapping(
                sector)[0]

            # retrieve sector periods
            periods = get_sector_periods(reg_id, child_locations)

            # set default period values when none is provided
            month_or_quarter, period = get_default_period(
                periods, month_or_quarter, period, True)

            # generate report period criteria
            criteria = build_report_period_criteria(month_or_quarter, period)

            sector_data[sector] = get_sector_data(reg_id,
                                                  report_id,
                                                  child_locations,
                                                  *criteria)
            sector_indicators[reg_id] = (
                constants.PERFORMANCE_INDICATOR_REPORTS[report_id])

            # populate selected sector variables
            selected_sector['sector'] = reg_id
            selected_sector['report'] = report_id
            selected_sector['label'] = label

            # retrieve project sector project geolocations
            geo_locations = json.dumps(
                get_geolocations_from_items(child_locations, reg_id))

            # generate chart_dataset
            chart_dataset = (
                build_performance_indicator_chart_dataset(
                    sector_indicators[reg_id], sector_data[sector]['rows']))

        else:
            # populate sector periods
            for reg_id, report_id, title in sectors:
                sector_periods = get_sector_periods(reg_id, child_locations)

                periods['years'].update(sector_periods['years'])
                periods['months'].update(sector_periods['months'])
                periods['quarters'].update(sector_periods['quarters'])

            # set default period values when none is provided
            month_or_quarter, period = get_default_period(
                periods, month_or_quarter, period, True)

            # generate report period criteria
            criteria = build_report_period_criteria(
                month_or_quarter, period)

            for reg_id, report_id, title in sectors:

                sector_data[reg_id] = get_sector_data(reg_id,
                                                      report_id,
                                                      child_locations,
                                                      *criteria)
                sector_indicators[reg_id] = (
                    constants.PERFORMANCE_INDICATOR_REPORTS[report_id])

        search_criteria = {'view_by': view_by,
                           'selected_sector': selected_sector,
                           'month_or_quarter': month_or_quarter,
                           'period': period,
                           'location': location}
        filter_criteria = Project.generate_filter_criteria()
        filter_criteria.update(periods)

        # return sectors, sector indicator list, sector indicator data.
        return {
            'sectors': sectors,
            'sector_indicators': sector_indicators,
            'sector_data': sector_data,
            'target_class': target_class,
            'search_criteria': search_criteria,
            'filter_criteria': filter_criteria,
            'location': location,
            'chart_dataset': chart_dataset,
            'geo_locations': geo_locations,
            self.PERFORMANCE_INDICATOR_EXPORT_KEY: True
        }

    @view_config(name='trends',
                 context=LocationFactory,
                 renderer='performance_indicators_trends.jinja2',
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

        # sort locations or projects by name
        child_locations.sort(key=lambda c: c.pretty)

        # Get periods based on the child locations
        # generate trend report for the selected sector
        sector = self.request.GET.get('sector') or None
        sectors = get_performance_sector_mapping()

        sector_id, report_id, label = get_performance_sector_mapping(sector)[0]

        periods = get_sector_periods(sector_id, child_locations)
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

        selected_sector = {}
        selected_sector['sector'] = sector_id
        selected_sector['report'] = report_id
        selected_sector['label'] = label

        indicators = get_performance_indicator_list(
            constants.PERFORMANCE_INDICATORS[report_id])

        sector_indicators = constants.PERFORMANCE_INDICATOR_REPORTS[report_id]

        # Generate trend report for all indicators
        series_data_map, series_labels = (
            get_performance_indicator_trend_report(
                sector_id,
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
                           'selected_sector': selected_sector,
                           'start_period': start_period,
                           'end_period': end_period,
                           'time_class': time_class,
                           'start_year': start_year,
                           'end_year': end_year,
                           'location': location or ''}

        filter_criteria = Project.generate_filter_criteria()

        filter_criteria.update(periods)

        return {
            'sectors': sectors,
            'chart_dataset': chart_dataset,
            'sector_indicators': sector_indicators,
            'search_criteria': search_criteria,
            'filter_criteria': filter_criteria,
            'time_series': time_series
        }

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
    build_performance_indicator_chart_dataset,
    generate_time_series,
    process_trend_parameters,
    get_child_locations,
    get_performance_indicator_trend_report)
from wkcdd.models import (
    County,
    Project,
    Report,
    Location)


@view_defaults(route_name='performance_indicators')
class PerformanceIndicators(object):

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
        else:
            location_ids = [c.id for c in County.all()]
            target_class = get_target_class_from_view_by(
                view_by, source_class)
            child_ids = get_children_by_level(
                location_ids, source_class, target_class)

            child_locations = target_class.all(target_class.id.in_(child_ids))

        # generate report period criteria
        criteria = build_report_period_criteria(month_or_quarter, period)

        # create a dict mapping to "property, key and type" based on
        # a selected sector or the first sector on the list

        if sector:
            # if the specified sector is not in location sector types
            # load all sectors
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

            # retrieve sector periods
            periods = get_sector_periods(reg_id, child_locations)

        else:
            # load first sector for the location list
            for reg_id, report_id, title in sectors:
                sector_data[reg_id] = get_sector_data(reg_id,
                                                      report_id,
                                                      child_locations,
                                                      *criteria)
                sector_indicators[reg_id] = (
                    constants.PERFORMANCE_INDICATOR_REPORTS[report_id])

                sector_periods = get_sector_periods(reg_id, child_locations)

                periods['years'].update(sector_periods['years'])
                periods['months'].update(sector_periods['months'])
                periods['quarters'].update(sector_periods['quarters'])

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
            'is_impact': False
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

        target_class = get_target_class_from_view_by(
            view_by, source_class)

        child_ids = get_children_by_level(
            location_ids, source_class, target_class)

        child_locations = target_class.all(target_class.id.in_(child_ids))

        # generate report period criteria
        criteria = build_report_period_criteria(month_or_quarter, period)

        # create a dict mapping to "property, key and type" based on
        # a selected sector or the first sector on the list
        if sector:
            # if the specified sector is not in location sector types
            # load all sectors
            reg_id, report_id, label = get_performance_sector_mapping(
                sector)[0]
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

            # retrieve sector periods
            periods = get_sector_periods(reg_id, child_locations)

        else:
            # load first sector for the location list
            for reg_id, report_id, title in sectors:
                sector_data[reg_id] = get_sector_data(reg_id,
                                                      report_id,
                                                      child_locations,
                                                      *criteria)
                sector_indicators[reg_id] = (
                    constants.PERFORMANCE_INDICATOR_REPORTS[report_id])

                sector_periods = get_sector_periods(reg_id, child_locations)

                periods['years'].update(sector_periods['years'])
                periods['months'].update(sector_periods['months'])
                periods['quarters'].update(sector_periods['quarters'])

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
            'is_impact': False
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

        # Get periods based on the child locations

        periods = Report.get_periods_for(child_locations)
        start_period, end_period, year = (
            process_trend_parameters(periods,
                                     self.request.GET.get('start_period'),
                                     self.request.GET.get('end_period'),
                                     self.request.GET.get('year')))

        # handle months or quarters
        time_class = self.request.GET.get('time_class', MONTH_PERIOD)

        # Generate time series range for the map x_axis

        time_series = generate_time_series(
            start_period, end_period, time_class, year)

        # generate trend report for the selected sector
        sector = self.request.GET.get('sector') or None
        sectors = get_performance_sector_mapping()

        sector_id, report_id, label = get_performance_sector_mapping(sector)[0]
        indicators = get_performance_indicator_list(
            constants.PERFORMANCE_INDICATORS[report_id])
        periods = get_sector_periods(sector_id, child_locations)

        # Generate trend report for all indicators

        series_data_map, series_labels = (
            get_performance_indicator_trend_report(
                time_series,
                time_class,
                year,
                indicators,
                child_locations))

        chart_dataset = json.dumps(
            {'labels': time_series,
             'series': series_data_map,
             'seriesLabels': series_labels})

        # update start period based on the retrieved data
        start_period = str(time_series[0]) if time_series else ''
        end_period = str(time_series[-1]) if time_series else ''

        search_criteria = {'view_by': view_by,
                           'start_period': start_period,
                           'end_period': end_period,
                           'time_class': time_class,
                           'year': year,
                           'location': location or ''}

        filter_criteria = Project.generate_filter_criteria()

        filter_criteria.update(periods)

        return {
            'sectors': sectors,
            'chart_dataset': chart_dataset,
            'indicators': indicators,
            'search_criteria': search_criteria,
            'filter_criteria': filter_criteria,
            'time_series': time_series
        }

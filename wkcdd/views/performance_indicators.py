from pyramid.view import (
    view_defaults,
    view_config
)

from wkcdd import constants
from wkcdd.models.location import LocationFactory
from wkcdd.models.helpers import get_children_by_level
from wkcdd.views.helpers import (
    get_sector_data,
    get_performance_sector_mapping,
    get_target_class_from_view_by,
    build_report_period_criteria)
from wkcdd.models import (
    County,
    Project,
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
        else:
            # load first sector for the location list
            for reg_id, report_id, title in sectors:
                sector_data[reg_id] = get_sector_data(reg_id,
                                                      report_id,
                                                      child_locations,
                                                      *criteria)
                sector_indicators[reg_id] = (
                    constants.PERFORMANCE_INDICATOR_REPORTS[report_id])

        search_criteria = {'view_by': view_by,
                           'selected_sector': selected_sector,
                           'location': ''}
        filter_criteria = Project.generate_filter_criteria()

        # return sectors, sector indicator list, sector indicator data.
        return {
            'sectors': sectors,
            'sector_indicators': sector_indicators,
            'sector_data': sector_data,
            'target_class': target_class,
            'search_criteria': search_criteria,
            'filter_criteria': filter_criteria,
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
        else:
            # load first sector for the location list
            for reg_id, report_id, title in sectors:
                sector_data[reg_id] = get_sector_data(reg_id,
                                                      report_id,
                                                      child_locations,
                                                      *criteria)
                sector_indicators[reg_id] = (
                    constants.PERFORMANCE_INDICATOR_REPORTS[report_id])

        search_criteria = {'view_by': view_by,
                           'selected_sector': selected_sector,
                           'location': location}
        filter_criteria = Project.generate_filter_criteria()

        # return sectors, sector indicator list, sector indicator data.
        return {
            'sectors': sectors,
            'sector_indicators': sector_indicators,
            'sector_data': sector_data,
            'target_class': target_class,
            'search_criteria': search_criteria,
            'filter_criteria': filter_criteria,
            'is_impact': False
        }
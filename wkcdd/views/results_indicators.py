
from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models import County, Report
from wkcdd.models.location import LocationFactory
from wkcdd.models.period import Period

from wkcdd.views.helpers import get_result_framework_indicators


@view_defaults(route_name='results_indicators')
class ResultsIndicators(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=LocationFactory,
                 renderer='results_indicators.jinja2',
                 request_method='GET')
    def index(self):
        quarter = self.request.GET.get('quarter', '')
        year = self.request.GET.get('year', '')

        period = Period(quarter, year)
        if not period:
            period = Period.latest_quarter()

        child_locations = County.all()

        indicators = get_result_framework_indicators(child_locations, period)

        search_criteria = {'month_or_quarter': quarter,
                           'period': period,
                           'location': ''}
        county_list = County.all()
        periods = Report.get_periods_for(child_locations)

        return {
            'indicators': indicators,
            'search_criteria': search_criteria,
            'counties': county_list,
            'periods': periods,
            'selected_quarter': quarter,
            'selected_year': year,
            'is_result_indicator': True
        }


from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models import County
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
        quarter = self.request.GET.get('month_or_quarter', '')
        period = self.request.GET.get('period', '')

        period = Period(quarter, period)
        if not period:
            period = Period.latest_quarter()

        child_locations = County.all()

        indicators = get_result_framework_indicators(child_locations, period)

        search_criteria = {'month_or_quarter': quarter,
                           'period': period,
                           'location': ''}
        county_list = County.all()

        return {
            'indicators': indicators,
            'search_criteria': search_criteria,
            'county_list': county_list,
            'is_result_indicator': True
        }

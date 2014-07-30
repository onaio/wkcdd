
from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models import SubCounty, Report
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
        county_id = self.request.GET.get('sub_county', '')
        selected_county = None

        period = Period(quarter, year)

        if year == '' and quarter == '':
            period = Period.latest_quarter()

        sub_counties = SubCounty.all()
        if county_id:
            selected_county = SubCounty.get(SubCounty.id == county_id)
            child_locations = [selected_county]
        else:
            child_locations = sub_counties

        indicators = get_result_framework_indicators(child_locations, period)

        search_criteria = {'month_or_quarter': quarter,
                           'month_or_quarter': period.quarter,
                           'period': period.year,
                           'location': selected_county}

        periods = Report.get_periods_for(child_locations)

        return {
            'indicators': indicators,
            'search_criteria': search_criteria,
            'sub_counties': sub_counties,
            'periods': periods,
            'is_result_indicator': True
        }

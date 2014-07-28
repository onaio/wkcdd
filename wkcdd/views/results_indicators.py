
from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models import County, Report, Project
from wkcdd.models.location import LocationFactory
from wkcdd.models.period import Period


@view_defaults(route_name='results_indicators')
class ResultIndicators(object):

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

        child_locations = County.all()

        indicators = Report.generate_report_indicators(
            child_locations, period)

        search_criteria = {'month_or_quarter': quarter,
                           'period': period,
                           'location': ''}
        filter_criteria = Project.generate_filter_criteria()

        return {
            'indicators': indicators,
            'search_criteria': search_criteria,
            'filter_criteria': filter_criteria,
            'is_result_indicator': True
        }

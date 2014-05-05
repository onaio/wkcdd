from pyramid.view import (
    view_defaults,
    view_config
)

from wkcdd import constants
from wkcdd.libs.utils import get_impact_indicator_list
from wkcdd.constants import IMPACT_INDICATOR_KEYS
from wkcdd.models import Report, County


@view_defaults(route_name='impact_indicators')
class ImpactIndicators(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 renderer='impact_indicators.jinja2',
                 request_method='GET')
    def show(self):
        indicators = get_impact_indicator_list(
            constants.IMPACT_INDICATOR_KEYS)

        # get list of locations
        # @todo: make dynamic depending on current location and view-by
        locations = County.all()
        rows, summary_row = Report.generate_impact_indicators(
            locations, indicators)

        return {
            'indicators': indicators,
            'rows': rows,
            'summary_row': summary_row
        }
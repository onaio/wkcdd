from pyramid.view import (
    view_defaults,
    view_config
)

from wkcdd.models.location import LocationFactory
from wkcdd.models.location import Location
from wkcdd.models.county import County
from wkcdd.models.sub_county import SubCounty
from wkcdd.models.report import Report
from wkcdd import constants
from wkcdd.views.helpers import build_dataset


@view_defaults(route_name='counties')
class CountyView(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=LocationFactory,
                 renderer='counties_list.jinja2',
                 request_method='GET')
    def show_all_counties(self):
        counties = County.all()
        impact_indicators = \
            Report.get_location_indicator_aggregation(counties)
        dataset = build_dataset(Location.COUNTY,
                                counties,
                                constants,
                                impact_indicators)
        return {
            'title': "County Impact Indicators Report",
            'headers': dataset['headers'],
            'rows': dataset['rows'],
            'summary_row': dataset['summary_row'],
        }

    @view_config(name='',
                 context=County,
                 renderer='county_sub_counties_list.jinja2',
                 request_method='GET')
    def list_all_sub_counties(self):
        county = self.request.context
        sub_counties = SubCounty.all(SubCounty.parent_id == county.id)

        impact_indicators = \
            Report.get_location_indicator_aggregation(sub_counties,
                                                      Location.COUNTY)
        dataset = build_dataset(Location.SUB_COUNTY,
                                sub_counties,
                                constants,
                                impact_indicators)

        return {
            'title': county.name,
            'headers': dataset['headers'],
            'rows': dataset['rows'],
            'summary_row': dataset['summary_row']
        }

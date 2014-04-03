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
from wkcdd.libs.utils import tuple_to_dict_list


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

        """
        impact_indicators
        ----------------
	impact_indicators['total_indicator_summary'][indicator.key]
       impact_indicators['aggregated_impact_indicators'][county.id]['summary'][indicator.key] 

        xls
	----
	headers = ['County', *loop over impact indicator titles]
        row = [(counties[0], loop over aggregated impact indicators), (...)]
        """

        headers = ["County"]
        headers.extend([t for t, k in constants.IMPACT_INDICATOR_REPORT])
        indicator_keys = [k for t, k in constants.IMPACT_INDICATOR_REPORT]
        rows = []

        for county in counties:
           row = [county.name] 
           row.extend([impact_indicators['aggregated_impact_indicators'][county.id]['summary'][key] for key in indicator_keys])
           rows.append(row)

	summary_row = []
	summary_row.extend([impact_indicators['total_indicator_summary'][key] for key in indicator_keys])	

        return {
            'title': "County Impact Indicators Report",
            'headers': headers,
            'rows': rows,
            'summary_row': summary_row,
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

        return {
            'county': county,
            'sub_counties': sub_counties,
            'impact_indicators': impact_indicators,
            'impact_indicator_mapping': tuple_to_dict_list(
                ('title', 'key'),
                constants.IMPACT_INDICATOR_REPORT)
        }


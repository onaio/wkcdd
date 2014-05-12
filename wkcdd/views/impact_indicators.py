from pyramid.view import (
    view_defaults,
    view_config
)

from wkcdd import constants
from wkcdd.models.helpers import get_children_by_level
from wkcdd.libs.utils import get_impact_indicator_list
from wkcdd.views.helpers import get_target_class_from_view_by
from wkcdd.models.location import LocationFactory
from wkcdd.models import (
    Report,
    County,
    Project,
    Location)


@view_defaults(route_name='impact_indicators')
class ImpactIndicators(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=LocationFactory,
                 renderer='impact_indicators.jinja2',
                 request_method='GET')
    def index(self):
        view_by = self.request.GET.get('view_by') or None

        source_class = County
        target_class = None

        if view_by is None or view_by == 'counties':
            child_locations = County.all()
        else:
            location_ids = [c.id for c in County.all()]
            target_class = get_target_class_from_view_by(
                view_by, source_class)
            child_ids = get_children_by_level(
                location_ids, source_class, target_class)

            child_locations = target_class.all(target_class.id.in_(child_ids))

        # create a dict mapping to "name, key and label"
        indicators = get_impact_indicator_list(
            constants.IMPACT_INDICATOR_KEYS)

        rows, summary_row = Report.generate_impact_indicators(
            child_locations, indicators)

        search_criteria = {'view_by': view_by,
                           'location': ''}
        filter_criteria = Project.generate_filter_criteria()

        return {
            'indicators': indicators,
            'rows': rows,
            'summary_row': summary_row,
            'target_class': target_class,
            'search_criteria': search_criteria,
            'filter_criteria': filter_criteria,
            'is_impact': True
        }

    @view_config(name='',
                 context=Location,
                 renderer='impact_indicators.jinja2',
                 request_method='GET')
    def show(self):
        view_by = self.request.GET.get('view_by') or None

        location = self.request.context
        source_class = location.__class__
        location_ids = [location.id]

        target_class = get_target_class_from_view_by(
            view_by, source_class)

        child_ids = get_children_by_level(
            location_ids, source_class, target_class)

        child_locations = target_class.all(target_class.id.in_(child_ids))
        # create a dict mapping to "name, key and label"
        indicators = get_impact_indicator_list(
            constants.IMPACT_INDICATOR_KEYS)

        rows, summary_row = Report.generate_impact_indicators(
            child_locations, indicators)

        search_criteria = {'view_by': view_by,
                           'location': location}
        filter_criteria = Project.generate_filter_criteria()

        return {
            'location': location,
            'indicators': indicators,
            'rows': rows,
            'summary_row': summary_row,
            'target_class': target_class,
            'search_criteria': search_criteria,
            'filter_criteria': filter_criteria,
            'is_impact': True
        }

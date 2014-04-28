from pyramid.view import (
    view_defaults,
    view_config
)
from wkcdd.models.community import Community
from wkcdd.models.report import Report
from wkcdd.views.helpers import build_dataset
from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list
from wkcdd.models import helpers


@view_defaults(route_name='community')
class CommunityView(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=Community,
                 renderer='community_projects_list.jinja2',
                 request_method='GET')
    def show(self):
        # TODO: eager load the constituency, county and sub-county
        # http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html#eager-loading
        # http://docs.sqlalchemy.org/en/rel_0_9/orm/relationships.html#self-referential-query-strategies # noqa
        community = self.request.context
        projects = community.projects
        impact_indicators = Report.get_aggregated_impact_indicators(projects)
        dataset = build_dataset("Project",
                                None,
                                impact_indicators,
                                projects
                                )

        return{
            'title': community.pretty,
            'headers': dataset['headers'],
            'rows': dataset['rows'],
            'summary_row': dataset['summary_row'],
            'community': community
        }

    @view_config(name='performance',
                 context=Community,
                 renderer='community_projects_performance_table.jinja2',
                 request_method='GET')
    def performance(self):
        community = self.request.context
        project_types_mappings = helpers.get_project_types([community.id])
        sector_indicator_mapping = {}
        sector_aggregated_indicators = {}
        for reg_id, report_id, title in project_types_mappings:
            total_aggregated_indicators = (
                Report.get_performance_indicator_aggregation_for(
                    [community], report_id))
            aggregated_indicators = (
                total_aggregated_indicators
                ['aggregated_performance_indicators']
                [community.id])
            indicator_mapping = tuple_to_dict_list(
                ('title', 'group'),
                constants.PERFORMANCE_INDICATOR_REPORTS[
                    report_id])
            sector_indicator_mapping[reg_id] = indicator_mapping
            sector_aggregated_indicators[reg_id] = aggregated_indicators
        return {
            'community': community,
            'project_types': project_types_mappings,
            'sector_aggregated_indicators': sector_aggregated_indicators,
            'sector_indicator_mapping': sector_indicator_mapping
        }

    def get_impact_indicators(self, projects):
        aggregated_indicators = (
            Report.get_impact_indicator_aggregation_for(projects))
        indicator_mapping = tuple_to_dict_list(
            ('title', 'key'),
            constants.IMPACT_INDICATOR_REPORT)
        return indicator_mapping, aggregated_indicators

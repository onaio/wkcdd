from pyramid.view import (
    view_config,
    view_defaults,
)

from wkcdd import constants

from wkcdd.models.report import Report, ReportFactory
from wkcdd.libs.utils import get_impact_indicator_list


@view_defaults(route_name='reports')
class ReportViews(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=ReportFactory,
                 renderer='reports_list.jinja2',
                 request_method='GET')
    def list(self):
        reports = Report.all(Report.status != Report.APPROVED)
        impact_indicator_mapping = get_impact_indicator_list(
            constants.IMPACT_INDICATOR_KEYS)
        performance_indicator_mappings = (
            constants.PERFORMANCE_INDICATOR_REPORTS)
        return {
            'reports': reports,
            'status_options': Report.status_labels,
            'impact_indicator_mapping': impact_indicator_mapping,
            'performance_indicator_mappings': performance_indicator_mappings
        }

    @view_config(name='update',
                 context=Report,
                 renderer='reports_list.jinja2',
                 request_method='POST')
    def update(self):
        report = self.request.context
        status = self.request.GET.get('status', '')
        if status:
            report.status = status
            report.save()
        return {
            'report': report
        }

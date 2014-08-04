from pyramid.view import (
    view_config,
    view_defaults,
)

from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPBadRequest
)

from wkcdd import constants
from wkcdd.views.helpers import report_submission_handler
from wkcdd.models.report import (
    Report,
    ReportFactory,
    ReportHandlerError

)
from wkcdd.libs.utils import get_impact_indicator_list


@view_defaults(route_name='reports')
class ReportViews(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=ReportFactory,
                 renderer='reports_list.jinja2',
                 request_method='GET',
                 permission='authenticated')
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
                 context=ReportFactory,
                 check_csrf=False,
                 request_method='POST',
                 permission='authenticated')
    def update(self):
        status = self.request.POST.get('new_status', 'pending')
        report_ids = self.request.POST.get('reports', '').split(",")
        # remove all null ids
        report_ids = filter(None, report_ids)
        reports = Report.all(Report.id.in_(report_ids))
        if reports and status:
            for report in reports:
                report.status = status
                report.save()

        url = self.request.route_url('reports', traverse=(''))

        return HTTPFound(location=url)

    @view_config(
        name='submissions',
        request_method='POST',
        context=ReportFactory)
    def json_post(self):
        payload = self.request.body
        if not payload:
            return HTTPBadRequest(comment='Missing JSON Payload')
        try:
            report_submission_handler(payload)
        except ReportHandlerError:
            return Response(
                'Accepted pending manual matching process', status=202)
        else:
            return Response('Saved', status=201)

from collections import OrderedDict
from pyramid.events import subscriber, NewRequest
from wkcdd import constants


@subscriber(NewRequest)
def requested_xlsx_format(event):
    request = event.request
    if request.GET.get('format') == 'xlsx':
        request.override_renderer = 'xlsx'
        return True


def build_dataset(location_type, locations, impact_indicators, projects=None):
    headers = [location_type]
    impact_indicator_report = OrderedDict(constants.IMPACT_INDICATOR_REPORT)
    headers.extend(impact_indicator_report.keys())
    indicator_keys = impact_indicator_report.values()

    rows = []
    summary_row = []

    if projects:
        for project_indicator in impact_indicators['indicator_list']:
            for project in projects:
                if project.id == project_indicator['project_id']:
                    row = [project]
            for key in indicator_keys:
                value = [0, 0, 0, 0] if project_indicator['indicators'] is \
                    None else project_indicator['indicators'][key]
                row.extend([value])
            rows.append(row)
        summary_row.extend([impact_indicators['summary']
                            [key] for key in indicator_keys])
    else:
        for location in locations:
            row = [location]
            row.extend([impact_indicators
                        ['aggregated_impact_indicators']
                        [location.id]['summary'][key]
                        for key in indicator_keys])
            rows.append(row)

        summary_row.extend([impact_indicators['total_indicator_summary']
                            [key] for key in indicator_keys])

    return{
        'headers': headers,
        'rows': rows,
        'summary_row': summary_row
    }

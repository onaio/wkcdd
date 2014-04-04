from pyramid.events import subscriber, NewRequest


@subscriber(NewRequest)
def requested_xlsx_format(event):
    request = event.request
    if request.GET.get('format') == 'xlsx':
        request.override_renderer = 'xlsx'
        return True


def build_dataset(location_type, locations, constants, impact_indicators):
    headers = [location_type]
    headers.extend([t for t, k in constants.IMPACT_INDICATOR_REPORT])
    indicator_keys = [k for t, k in constants.IMPACT_INDICATOR_REPORT]
    rows = []

    for location in locations:
        row = [location]
        row.extend([impact_indicators['aggregated_impact_indicators']
                    [location.id]['summary'][key] for key in indicator_keys])
        rows.append(row)

    summary_row = []
    summary_row.extend([impact_indicators['total_indicator_summary']
                        [key] for key in indicator_keys])

    return{
        'headers': headers,
        'rows': rows,
        'summary_row': summary_row
    }

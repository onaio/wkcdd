import tablib


class TablibRenderer(object):

    def __init__(self, info):  # noqa
        pass

    def initialize_dataset(self, value, system):  # noqa
        title = None
        headers = None
        rows = None
        summary_row = None

        if value.get('is_impact'):
            # Generate dataset for impact indicators
            title, headers, rows, summary_row = (
                self.generate_impact_indicator_dataset(value))
        else:
            # Generate dataset for performance indicators
            title, headers, rows, summary_row = (
                self.generate_performance_indicator_dataset(value))

        dataset = tablib.Dataset(headers)
        dataset.title = title
        for row in rows:
            dataset.append(row)
        # prepend a summary title to the summary row
        summary_row[:0] = ['Total Summary']
        dataset.append(summary_row)
        return dataset

    def generate_impact_indicator_dataset(self, value):
        indicators = value.get('indicators')
        rows = value.get('rows')
        summary_row = value.get('summary_row')
        location = value.get('location')

        title = location.pretty if location else "Summary Report"
        headers = ["Name"] + [item['label'] for item in indicators]
        dataset_rows = []
        indicator_keys = [item['key'] for item in indicators]
        for row in rows:
            dataset_row = [row['location'].pretty]
            dataset_row.extend(
                [row['indicators'][key] for key in indicator_keys])
            dataset_rows.append(dataset_row)
        dataset_summary_row = [summary_row[key]
                               for key in indicator_keys]

        return title, headers, dataset_rows, dataset_summary_row

    def generate_performance_indicator_dataset(self, value):
        selected_sector = (
            value.get('search_criteria').get('selected_sector').get('sector'))

        selected_sector_data = value.get('sector_data').get(selected_sector)
        indicators = value.get('sector_indicators').get(selected_sector)
        rows = selected_sector_data.get('rows')
        summary_row = selected_sector_data.get('summary_row')
        location = value.get('location')

        title = location.pretty if location else "Summary Report"

        headers = ["Name"] + [label for label, key_group in indicators]
        dataset_rows = []
        indicator_keys = [key_group for label, key_group in indicators]

        for row in rows:
            dataset_row = [row['location'].pretty]
            dataset_row.extend(
                ["{:.2f}% ({}/{})".format(row['indicators'].get(percentage, 0),
                                          row['indicators'].get(actual, 0),
                                          row['indicators'].get(target, 0))
                 if percentage and target
                 else "{}".format(row['indicators'].get(actual, 0))
                 for target, actual, percentage in indicator_keys])
            dataset_rows.append(dataset_row)
        dataset_summary_row = (
            ["{:.2f}% ({}/{})".format(summary_row.get(percentage, 0),
                                      summary_row.get(actual, 0),
                                      summary_row.get(target, 0))
             if percentage and target
             else "{}".format(row['indicators'].get(actual, 0))
             for target, actual, percentage in indicator_keys])

        return title, headers, dataset_rows, dataset_summary_row

    def __call__(self, value, system):
        raise NotImplementedError("Use a specific subclass")


class TablibXLSXRenderer(TablibRenderer):
    extension = 'xlsx'

    def __call__(self, value, system):
        dataset = self.initialize_dataset(value, system)
        request = system['request']
        response = request.response
        response.content_type = \
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.content_disposition = "attachment; filename={}.{}".format(
            dataset.title, self.extension)
        return dataset.xlsx

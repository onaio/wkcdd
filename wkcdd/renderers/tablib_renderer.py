import tablib


class TablibRenderer(object):
    def __init__(self, info):  # noqa
        pass

    def initialize_dataset(self, value, system):  # noqa
        dataset = tablib.Dataset(headers=value['headers'])
        dataset.title = value.get('title', "report")
        for row in value['rows']:
            dataset.append(row)
        summary_row = value['summary_row']
        # prepend a summary title to the summary row
        summary_row[:0] = ['Total Summary']
        dataset.append(summary_row)
        return dataset

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
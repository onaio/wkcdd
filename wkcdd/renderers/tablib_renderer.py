import tablib

from wkcdd import constants


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
        elif value.get('is_project_export'):
            title, headers, rows, summary_row = (
                self.generate_project_mis_export(value))
        elif value.get('is_report_export'):
            title, headers, rows, summary_row = (
                self.generate_mis_project_indicator_reports(value))
        else:
            # Generate dataset for performance indicators
            title, headers, rows, summary_row = (
                self.generate_performance_indicator_dataset(value))

        dataset = tablib.Dataset(headers)
        dataset.title = title

        for row in rows:
            dataset.append(row)

        # prepend a summary title to the summary row
        if summary_row:
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

    def generate_project_mis_export(self, value):
        projects = value.get('projects')
        title = "MIS Project Export"
        headers = []
        rows = []
        summary_row = []
        if projects:
            headers = ["ProjectID", "StartDate", "Name", "County",
                       "SubCounty", "Constituency", "Community", "Sector",
                       "Category", "Chairman", "Cno", "Secretary",
                       "Sno", "Treasurer", "Tno"]

            for project in projects:
                row = []
                row.append(project.code.upper())
                row.append(project.start_date)
                row.append(project.name)

                community = project.community
                constituency = community.constituency
                sub_county = constituency.sub_county
                county = sub_county.county
                row.append(county.get_mis_code())
                row.append(sub_county.get_mis_code())
                row.append(constituency.get_mis_code())
                row.append(community.get_mis_code())

                row.append(project.mis_sector_code)
                row.append(project.project_type.name.upper())

                row.append(project.chairperson)
                row.append(project.chairperson_phone_number)

                row.append(project.secretary)
                row.append(project.secretary_phone_number)

                row.append(project.treasurer)
                row.append(project.treasurer_phone_number)

                rows.append(row)

            return title, headers, rows, summary_row
        else:
            raise ValueError("No projects to generate MIS report")

    def generate_mis_project_indicator_reports(self, value):
        reports = value.get('reports')
        title = "MIS Indicator Export"
        headers = []
        rows = []
        summary_row = []

        if reports:
            # generate MIS reports based on the agreed format.
            headers = ["Community", "ProjectID", "IndicatorCode",
                       "Expected", "Actual", "Month", "Year"]

            for report in reports:
                project = report.project

                # Skip reports without a valid project entry

                if project is None:
                    continue

                # Add function for retrieving list of report indicator values
                indicators = report.get_performance_indicators()
                indicator_mapping = (
                    constants.PERFORMANCE_INDICATOR_REPORTS[report.form_id])

                for label, keys in indicator_mapping:
                    row = []
                    row.append(project.community.get_mis_code())
                    row.append(project.code.upper())

                    # generate indicator key in a fancy way e.g. Community
                    # Contribution = CC
                    row.append(label)

                    expected_value_key = keys[0]
                    actual_value_key = keys[1]

                    row.append(indicators[expected_value_key])
                    row.append(indicators[actual_value_key])
                    row.append(report.month)
                    row.append(report.period)

                    rows.append(row)

            return title, headers, rows, summary_row
        else:
            raise ValueError("No reports to generate MIS report")

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

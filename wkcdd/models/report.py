
from collections import defaultdict

from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list
from wkcdd.models.project import Project

from wkcdd.models.base import (
    Base,
    DBSession
)
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String
)
from sqlalchemy.dialects.postgresql import JSON

from wkcdd.libs.utils import (
    get_impact_indicator_list,
    sum_reduce_func)
from wkcdd.models.helpers import (
    get_project_list,
    get_community_ids_for,
)


class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True, nullable=False)
    project_code = Column(String, nullable=False, index=True)
    submission_time = Column(DateTime(timezone=True), nullable=False)
    month = Column(Integer, nullable=False)
    quarter = Column(String, nullable=False)
    period = Column(String, nullable=False)
    report_data = Column(JSON, nullable=False)

    @classmethod
    def add_report_submission(cls, report):
        report.save()

    # TODO rename to get_impact_indicators
    def calculate_impact_indicators(self):
        indicators = get_impact_indicator_list(
            constants.IMPACT_INDICATOR_KEYS)
        impact_indicators = {
            item['key']: self.report_data.get(item['key'])
            for item in indicators}
        return impact_indicators

    # TODO rename to get_performance_indicators
    def calculate_performance_indicators(self):
        performance_indicators = defaultdict(int)
        set_value = lambda value: (0 if value is None
                                   or value == 'Infinity'
                                   else value)
        for key, performance_indicator_key\
            in constants.PERFORMANCE_INDICATORS[self.report_data[
                constants.XFORM_ID]]:
            if type(performance_indicator_key) == list:
                for key_instance in performance_indicator_key:
                    if not performance_indicators[key]:
                        performance_indicators[key] = set_value(
                            self.report_data.get(key_instance))
            else:
                performance_indicators[key] = set_value(
                    self.report_data.get(performance_indicator_key))
        return performance_indicators

    @classmethod
    def get_aggregated_impact_indicators(cls, project_list):
        """
        Returns a compiled list of impact or performance indicators from
        the supplied project list.
        returns {
            'indicator_list': [
                {
                    'project_name': project_name_a,
                    'project_code': project_code,
                    'indicators': indicators_for_project_a
                },
                {
                    'name': project_name_b
                    'indicators': indicators_for_project_b
                }
            ],
            'summary': {sum_of_all_individual_indicators}
        }
        """

        indicator_list = []
        summary = defaultdict(lambda: 0)
        for project in project_list:
            report = project.get_latest_report()
            if report:
                p_impact_indicators = (
                    report.calculate_impact_indicators())
                for key, value in p_impact_indicators.items():
                    value = 0 if value is None else value
                    summary[key] += int(value)
                project_indicators_map = {
                    'project_name': project.name,
                    'project_id': project.id,
                    'indicators': p_impact_indicators
                }
            else:
                project_indicators_map = {
                    'project_name': project.name,
                    'project_id': project.id,
                    'indicators': None
                }
            indicator_list.append(project_indicators_map)
        return {
            'indicator_list': indicator_list,
            'summary': summary
        }

    @classmethod
    def get_aggregated_performance_indicators(cls, project_list, project_type):
        indicator_list = []
        summary = defaultdict(int)
        summary_report_count = 0
        if project_list:
            indicator_list = []
            summary = defaultdict(int)
            for project in project_list:
                report = project.get_latest_report()
                if report:
                    p_impact_indicators = (
                        report.calculate_performance_indicators())
                    for key, value in p_impact_indicators.items():
                        value = (0 if value is None or value == 'Infinity'
                                 else value)
                        summary[key] += int(value)
                    project_indicators_map = {
                        'project_name': project.name,
                        'project_id': project.id,
                        'indicators': p_impact_indicators
                    }
                    summary_report_count += 1
                else:
                    project_indicators_map = {
                        'project_name': project.name,
                        'project_id': project.id,
                        'indicators': None
                    }
                indicator_list.append(project_indicators_map)
        if summary:
            Report.average_performance_ratios(project_type,
                                              summary,
                                              summary_report_count)
        return {
            'indicator_list': indicator_list,
            'summary': summary
        }

    @classmethod
    def get_impact_indicator_aggregation_for(cls, child_locations):
        impact_indicator_mapping = tuple_to_dict_list(
            ('title', 'key'), constants.IMPACT_INDICATOR_REPORT)

        impact_indicators = {}
        total_indicator_summary = defaultdict(int)
        for child_location in child_locations:
            projects = Report.get_projects_from_location(child_location)
            indicators = Report.get_aggregated_impact_indicators(projects)
            impact_indicators[child_location.id] = indicators
            for indicator in impact_indicator_mapping:
                total_indicator_summary[indicator['key']] += (
                    impact_indicators[child_location.id]
                    ['summary'][indicator['key']])

        return {
            'aggregated_impact_indicators': impact_indicators,
            'total_indicator_summary': total_indicator_summary
        }

    @classmethod
    def get_projects_from_location(cls,
                                   location,
                                   *criteria):
        community_ids = get_community_ids_for(type(location), [location.id])
        projects = get_project_list(community_ids, *criteria)
        return projects

    @classmethod
    def average_performance_ratios(cls,
                                   report_type,
                                   summary,
                                   summary_report_count):
        mapping = tuple_to_dict_list(
            ('title', 'group'),
            constants.PERFORMANCE_INDICATOR_REPORTS[report_type])
        percentage_mapping = [indicator['group'][2]
                              for indicator in mapping
                              if indicator['group'][2]]
        for field in percentage_mapping:
            percent = (float(summary[field]) /
                       float(summary_report_count))
            summary[field] = percent

    @classmethod
    def get_performance_indicator_aggregation_for(cls,
                                                  child_locations,
                                                  report_type,
                                                  location_type="All"):
        mapping = tuple_to_dict_list(
            ('title', 'group'),
            constants.PERFORMANCE_INDICATOR_REPORTS[report_type])
        project_type = [project_type for project_type, report_id, label in
                        constants.PROJECT_TYPE_MAPPING
                        if report_id == report_type][0]
        performance_indicators = {}
        total_indicator_summary = defaultdict(int)
        location_count = len(child_locations)
        project_list = []
        for child_location in child_locations:
            projects = Report.get_projects_from_location(
                child_location,
                (Project.sector == project_type))
            project_list = project_list + projects
            indicators = Report.get_aggregated_performance_indicators(
                projects, report_type)
            performance_indicators[child_location.id] = indicators
            for indicator in mapping:
                for field in indicator['group']:
                    summary = (performance_indicators[child_location.id]
                               ['summary'])
                    if summary:
                        value = summary.get(field) or 0
                        total_indicator_summary[field] += value

        if total_indicator_summary:
            Report.average_performance_ratios(report_type,
                                              total_indicator_summary,
                                              location_count)

        return {
            'aggregated_performance_indicators': performance_indicators,
            'total_indicator_summary': total_indicator_summary,
            'project_list': project_list
        }

    @classmethod
    def get_reports_for_projects(cls, projects):
        """
        Get the reports for the specified list of projects.
        """
        if projects:
            return DBSession.query(Report)\
                .join(Project, Report.project_code == Project.code)\
                .filter(Project.id.in_([p.id for p in projects]))\
                .all()
        else:
            raise ReportError("No projects provided")

    @classmethod
    def sum_impact_indicator_values(cls, indicator_key, reports):
        """
        Calculate the sum for the specified indicator from the reports
        """
        values = [r.report_data.get(indicator_key) for r in reports]
        return reduce(
            sum_reduce_func, values, 0)

    @classmethod
    def generate_impact_indicators(cls, collection, indicators):
        """
        Generate impact indicators for a given collection where the
        collection can either be a list of projects or a list of locations
        """
        rows = []
        summary_row = dict([(indicator['key'], 0) for indicator in indicators])
        for item in collection:
            row = {
                'location': item,
                'indicators': {}
            }
            # get reports for this location or project,
            projects = item.get_projects()

            # get project reports @todo: filtered by said period
            reports = cls.get_reports_for_projects(projects)

            for indicator in indicators:
                indicator_key = indicator['key']
                location_indicator_sum = cls.sum_impact_indicator_values(
                    indicator_key, reports)
                row['indicators'][indicator_key] = location_indicator_sum

                # sum the summary
                summary_row[indicator_key] += location_indicator_sum

            # append row
            rows.append(row)

        return rows, summary_row

    @classmethod
    def sum_performance_indicator_values(cls,
                                         indicator_key,
                                         indicator_type,
                                         reports):
        """
        Calculate the sum and average for the specified indicator from the
        reports
        """
        values = []
        # handle keys which are lists due to legacy form submissions
        if reports:
            try:
                values = [r.report_data.get(indicator_key) for r in reports]
            except TypeError:
                for key in indicator_key:
                    values.extend(
                        [r.report_data.get(key) for r in reports])
            finally:
                if indicator_type == 'ratio':
                    return (float(
                            reduce(
                                sum_reduce_func, values, 0))
                            /
                            float(
                                len(reports)))
                else:
                    return reduce(
                        sum_reduce_func, values, 0)
        else:
            raise ValueError("No reports provided")

    @classmethod
    def generate_performance_indicators(cls,
                                        collection,
                                        indicators,
                                        *criteria):
        """
        Generate performance indicators for a given sector whose values are
        determined from the provided set of indicators
        """
        rows = []
        summary_row = defaultdict(int)
        for item in collection:
            try:
                row = {
                    'location': item,
                    'indicators': {}
                }
                # get reports for this location or project,
                projects = item.get_projects(*criteria)
                # get project reports @todo: filtered by said period
                reports = cls.get_reports_for_projects(projects)

                for indicator in indicators:
                    indicator_key = indicator['key']
                    indicator_property = indicator['property']
                    indicator_type = indicator['type']

                    try:
                        location_indicator_sum = (
                            cls.sum_performance_indicator_values(
                                indicator_key, indicator_type, reports))
                    except ValueError:
                        location_indicator_sum = 0

                    row['indicators'][
                        indicator_property] = location_indicator_sum

                    # sum the summary
                    summary_row[indicator_property] += location_indicator_sum

                # append row
                rows.append(row)
            except ReportError:
                # Catch case where there are no projects matching the criteria
                pass

        # get summary row averages for ratio fields
        for indicator in indicators:
            indicator_type = indicator['type']
            indicator_property = indicator['property']

            if indicator_type == 'ratio':
                summary_row[indicator_property] = (
                    summary_row[indicator_property] / len(collection))

        return rows, summary_row


class ReportError(Exception):
    pass

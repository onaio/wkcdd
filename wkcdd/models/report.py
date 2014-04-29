from collections import defaultdict

from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list
from wkcdd.models.project import Project

from wkcdd.models.base import (
    Base
)
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String
)
from sqlalchemy.dialects.postgresql import JSON
from wkcdd.models.helpers import (
    get_project_list,
    get_community_ids_for
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
        impact_indicators = {}
        for key, impact_indicator_key in constants.IMPACT_INDICATOR_KEYS:
            impact_indicators[key] = self.report_data.get(impact_indicator_key)
        return impact_indicators

    # TODO rename to get_performance_indicators
    def calculate_performance_indicators(self):
        performance_indicators = defaultdict(int)
        for key, performance_indicator_key\
            in constants.PERFORMANCE_INDICATORS[self.report_data[
                constants.XFORM_ID]]:
            if type(performance_indicator_key) == list:
                for key_instance in performance_indicator_key:
                    if not performance_indicators[key]:
                        performance_indicators[key] = (
                            self.report_data.get(key_instance))
            else:
                performance_indicators[key] = (
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
        for child_location in child_locations:
            projects = Report.get_projects_from_location(
                child_location,
                (Project.sector == project_type))
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
            'total_indicator_summary': total_indicator_summary
        }

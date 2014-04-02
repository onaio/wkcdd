from collections import defaultdict

from wkcdd import constants

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

    def calculate_impact_indicators(cls):
        impact_indicators = {}
        for key, impact_indicator_key in constants.IMPACT_INDICATOR_KEYS:
            impact_indicators[key] = cls.report_data.get(impact_indicator_key)
        return impact_indicators

    def calculate_performance_indicators(cls):
        performance_indicators = {}
        for key, performance_indicator_key\
            in constants.PERFORMANCE_INDICATORS[cls.report_data[
                constants.XFORM_ID]]:
            performance_indicators[key] = cls.\
                report_data.get(performance_indicator_key)
        return performance_indicators

    @classmethod
    def get_aggregated_project_indicators(cls, project_list, is_impact=True):
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
        indicator_list = None
        summary = None
        if project_list:
            indicator_list = []
            summary = defaultdict(int)
            for project in project_list:
                report = project.get_latest_report()
                if report:
                    if is_impact:
                        p_impact_indicators = (
                            report.calculate_impact_indicators())
                        for key, value in p_impact_indicators.items():
                            value = 0 if value is None else value
                            summary[key] += int(value)
                    else:
                        p_impact_indicators = (
                            report.calculate_performance_indicators())
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

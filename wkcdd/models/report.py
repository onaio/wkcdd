from collections import defaultdict

from wkcdd import constants
from wkcdd.libs.utils import tuple_to_dict_list
from wkcdd.models import Location

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
from wkcdd.models.utils import (
    get_project_list,
    get_community_ids,
    get_constituency_ids,
    get_sub_county_ids
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
        indicator_list = []
        summary = defaultdict(lambda: 0)
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

    @classmethod
    def get_location_indicator_aggregation(cls,
                                           child_locations,
                                           location_type="All"):
        impact_indicator_mapping = tuple_to_dict_list(
            ('title', 'key'), constants.IMPACT_INDICATOR_REPORT)

        impact_indicators = {}
        total_indicator_summary = defaultdict(int)
        for child_location in child_locations:
            if location_type == Location.CONSTITUENCY:
                # Child location is community
                projects = get_project_list([child_location.id])
            elif location_type == Location.SUB_COUNTY:
                # Child location is constituency
                projects = get_project_list(
                    get_community_ids([child_location.id]))
            elif location_type == Location.COUNTY:
                # Child location is sub_county
                projects = get_project_list(get_community_ids
                                            (get_constituency_ids
                                             ([child_location.id])))
            elif location_type == "All":
                # child location == county
                projects = get_project_list(get_community_ids
                                            (get_constituency_ids
                                             (get_sub_county_ids
                                              ([child_location.id]))))
            else:
                raise ValueError(
                    "cant determine location type '{}'".format(location_type))

            indicators = Report.get_aggregated_project_indicators(projects)
            impact_indicators[child_location.id] = indicators
            # TODO: this raises an exception if projects is empty
            for indicator in impact_indicator_mapping:
                total_indicator_summary[indicator['key']] += (
                    impact_indicators[child_location.id]
                    ['summary'][indicator['key']])

        return {
            'aggregated_impact_indicators': impact_indicators,
            'total_indicator_summary': total_indicator_summary
        }

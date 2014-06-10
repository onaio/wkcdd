
from collections import defaultdict

from wkcdd import constants
from wkcdd.models.project import Project

from wkcdd.models.base import (
    Base,
    DBSession,
    BaseModelFactory
)
from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    Enum,
    desc
)
from sqlalchemy.dialects.postgresql import JSON

from wkcdd.libs.utils import (
    get_impact_indicator_list,
    sum_reduce_func)


class Report(Base):
    __tablename__ = 'reports'

    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    id = Column(Integer, primary_key=True, nullable=False)
    project_code = Column(String, nullable=False, index=True)
    submission_time = Column(DateTime(timezone=True), nullable=False)
    month = Column(Integer, nullable=False)
    quarter = Column(String, nullable=False)
    period = Column(String, nullable=False)

    report_data = Column(JSON, nullable=False)

    status = Column(
        Enum(PENDING, APPROVED, REJECTED, name='SUBMISSION_STATUS'),
        nullable=False, index=True, default=PENDING)

    status_labels = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    )

    @property
    def form_id(self):
        return self.report_data[constants.XFORM_ID]

    @property
    def project(self):
        # since projects can have the same code, return the first one
        return Project.all(Project.code == self.project_code)[0]

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
        for key, performance_indicator_key, indicator_type\
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
    def get_year_interval(cls, start_year, end_year):
        results = DBSession.query(Report.period)\
            .filter(Report.period.between(start_year, end_year))\
            .group_by(Report.period)\
            .all()
        return results

    @classmethod
    def get_month_interval(cls,
                           start_period,
                           end_period,
                           start_year,
                           end_year):
        results = DBSession.query(Report.month, Report.period)\
            .filter(Report.period.between(start_year, end_year))\
            .filter(Report.month.between(start_period, end_period))\
            .group_by(Report.month, Report.period)\
            .order_by(Report.period, Report.month)\
            .all()

        return results

    @classmethod
    def get_quarter_interval(cls,
                             start_period,
                             end_period,
                             start_year,
                             end_year):
        results = DBSession.query(Report.quarter, Report.period)\
            .filter(Report.period.between(start_year, end_year))\
            .filter(Report.quarter.between(start_period, end_period))\
            .group_by(Report.quarter, Report.period)\
            .order_by(Report.period, Report.quarter)\
            .all()

        return results

    @classmethod
    def get_latest_month_for_year(cls, year):
        results = DBSession.query(Report.month)\
            .filter(Report.period == year)\
            .group_by(Report.month)\
            .order_by(desc(Report.month))\
            .first()

        return results

    @classmethod
    def get_reports_for_projects(cls, project_ids, *criteria):
        """
        Get the reports for the specified list of projects based on the
        specified time period
        Projects is a tuple list containing id and project code
        """
        if project_ids:
            return DBSession.query(Report)\
                .join(Project, Report.project_code == Project.code)\
                .filter(Project.id.in_(project_ids))\
                .filter(Report.status == Report.APPROVED)\
                .filter(*criteria)\
                .order_by(Report.submission_time)\
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
    def generate_impact_indicators(cls, collection, indicators, *criteria):
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
            projects = item.get_project_ids()

            # get project reports @todo: filtered by said period
            try:
                reports = cls.get_reports_for_projects(projects, *criteria)

                for indicator in indicators:
                    indicator_key = indicator['key']
                    location_indicator_sum = cls.sum_impact_indicator_values(
                        indicator_key, reports)
                    row['indicators'][indicator_key] = location_indicator_sum

                    # sum the summary
                    summary_row[indicator_key] += location_indicator_sum
            except ReportError:
                pass
            # append row
            rows.append(row)

        return rows, summary_row

    @classmethod
    def sum_performance_indicator_values(cls,
                                         indicator_key,
                                         reports):
        """
        Calculate the sum and average for the specified indicator from the
        reports
        """
        values = []

        if reports:
            try:
                values = [r.report_data.get(indicator_key) for r in reports]
            except TypeError:
                # handle legacy form submissions
                for key in indicator_key:
                    values.extend(
                        [r.report_data.get(key) for r in reports])
            finally:
                return reduce(
                    sum_reduce_func, values, 0)
        else:
            raise ValueError("No reports provided")

    @classmethod
    def calculate_ratio_value(cls, actual_value, expected_value):
        if actual_value and expected_value:
            return round(
                float(actual_value) / float(expected_value) * 100, 2)
        else:
            return 0

    @classmethod
    def generate_performance_indicators(cls,
                                        collection,
                                        indicators,
                                        **kwargs):
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
                project_filter_criteria = kwargs.get(
                    'project_filter_criteria', [])
                projects = item.get_project_ids(project_filter_criteria)

                # filter reports by period
                period_criteria = kwargs.get('period_criteria', [])
                reports = cls.get_reports_for_projects(
                    projects,
                    *period_criteria)

                for index, indicator in enumerate(indicators):
                    indicator_key = indicator['key']
                    indicator_property = indicator['property']
                    indicator_type = indicator['type']

                    if indicator_type == 'ratio':
                        # retrieve the last two calculated values and divide
                        target_property = indicators[index - 2]['property']
                        actual_property = indicators[index - 1]['property']

                        target_value = row['indicators'].get(target_property)
                        actual_value = row['indicators'].get(actual_property)

                        location_indicator_sum = cls.calculate_ratio_value(
                            actual_value, target_value)
                    else:
                        try:
                            location_indicator_sum = (
                                cls.sum_performance_indicator_values(
                                    indicator_key, reports))
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
        for index, indicator in enumerate(indicators):
            indicator_type = indicator['type']
            indicator_property = indicator['property']

            if indicator_type == 'ratio':
                target_property = indicators[index - 2]['property']
                actual_property = indicators[index - 1]['property']
                target_value = summary_row.get(target_property)
                actual_value = summary_row.get(actual_property)

                summary_row[indicator_property] = cls.calculate_ratio_value(
                    actual_value, target_value)

        return rows, summary_row

    @classmethod
    def get_periods_for(cls, collection, *project_filter_criteria):
        periods = defaultdict(set)

        for item in collection:
            try:
                projects = item.get_project_ids(*project_filter_criteria)
                reports = cls.get_reports_for_projects(projects)
                # retrieve periods based on the reports available
                cls.generate_periods_from_reports(periods, reports)

            except ReportError:
                pass

        return periods

    @classmethod
    def generate_periods_from_reports(cls, periods, reports):
        periods['years'].update({report.period for report in reports})
        periods['months'].update({report.month for report in reports})
        periods['quarters'].update(
            {report.quarter for report in reports})

    @classmethod
    def get_trend_values_for_impact_indicators(cls,
                                               collection,
                                               indicator_key,
                                               *time_criteria):
        indicator_values = []
        for item in collection:
            try:
                projects = item.get_project_ids()
                reports = cls.get_reports_for_projects(
                    projects,
                    *time_criteria)
                indicator_sum = cls.sum_impact_indicator_values(
                    indicator_key, reports)
                indicator_values.append(indicator_sum)
            except ReportError:
                indicator_values.append(0)

        return indicator_values

    @classmethod
    def get_trend_values_for_performance_indicators(cls,
                                                    collections,
                                                    indicators,
                                                    period_label,
                                                    **kwargs):
        project_filter_criteria = kwargs.get('project_filter_criteria', [])
        time_criteria = kwargs.get('time_criteria', [])
        series_map = {}

        for item in collections:
            try:
                projects = item.get_project_ids(project_filter_criteria)
                reports = cls.get_reports_for_projects(
                    projects,
                    *time_criteria)
                series_data = {}
                indicator_values = {}

                for index, indicator in enumerate(indicators):
                    # Need to group into target, actual, ratio key groups
                    indicator_type = indicator['type']
                    indicator_property = indicator['property']
                    indicator_key = indicator['key']

                    if indicator_type == 'ratio':
                        target_property = indicators[index - 2]['property']
                        actual_property = indicators[index - 1]['property']

                        actual_value = indicator_values[actual_property]
                        target_value = indicator_values[target_property]

                        ratio = cls.calculate_ratio_value(
                            actual_value, target_value)
                        series_data[indicator_property] = (
                            [period_label, ratio])
                    else:
                        try:
                            indicator_sum = (
                                cls.sum_performance_indicator_values(
                                    indicator_key, reports))
                        except ValueError:
                            indicator_sum = 0

                        indicator_values[indicator_property] = indicator_sum

            except ReportError:
                series_data = {indicator['property']: 0
                               for indicator in indicators}

            series_map[item.pretty] = series_data

        return series_map


class ReportError(Exception):
    pass


class ReportHandlerError(Exception):
    pass


class ReportFactory(BaseModelFactory):
    __acl__ = []

    def __getitem__(self, item):
        # try to retrieve the report whose id matches item
        try:
            report_id = int(item)
            report = DBSession.query(Report).filter_by(id=report_id).one()
        except (ValueError, NoResultFound):
            raise KeyError
        else:
            report.__parent__ = self
            report.__name__ = item
            return report

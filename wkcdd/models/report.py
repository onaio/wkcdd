
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
    Enum
)
from sqlalchemy.dialects.postgresql import JSON

from wkcdd.libs.utils import get_impact_indicator_list


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
    def get_reports_for_projects(cls, projects, *criteria):
        """
        Get the reports for the specified list of projects based on the
        specified time period
        """
        if projects:
            return DBSession.query(Report)\
                .join(Project, Report.project_code == Project.code)\
                .filter(Project.id.in_([p.id for p in projects]))\
                .filter(Report.status == Report.APPROVED)\
                .filter(*criteria)\
                .order_by(Report.submission_time)\
                .all()
        else:
            raise ReportError("No projects provided")

    @classmethod
    def sum_indicator_values(cls, indicator_key, reports):
        """
        Calculate the sum for the specified indicator from the reports
        """
        report_ids = [r.id for r in reports]
        if report_ids:
            total = DBSession.query('total').from_statement(
                "Select SUM((report_data->>:key)::integer) as total \
                FROM reports where report_data->>:key <> 'Infinity'\
                and id in :list").params(
                key=indicator_key, list=tuple(report_ids)).first()
            return total[0] or 0
        else:
            return 0

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
            projects = item.get_projects()

            # get project reports @todo: filtered by said period
            try:
                reports = cls.get_reports_for_projects(projects, *criteria)

                for indicator in indicators:
                    indicator_key = indicator['key']
                    location_indicator_sum = cls.sum_indicator_values(
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
                                         indicator_type,
                                         reports):
        """
        Calculate the sum and average for the specified indicator from the
        reports
        """
        total = 0

        if reports:
            # handle keys which are lists due to legacy form submissions
            if isinstance(indicator_key, list):
                # Find sum for all values
                for key in indicator_key:
                    total += cls.sum_indicator_values(key, reports)
            else:
                total += cls.sum_indicator_values(indicator_key, reports)

            if indicator_type == 'ratio':
                return float(total) / float(len(reports))
            else:
                return total
        else:
            raise ValueError("No reports provided")

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
                projects = item.get_projects(project_filter_criteria)

                # filter reports by period
                period_criteria = kwargs.get('period_criteria', [])
                reports = cls.get_reports_for_projects(
                    projects,
                    *period_criteria)

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

    @classmethod
    def get_periods_for(cls, collection, *project_filter_criteria):
        periods = defaultdict(set)

        for item in collection:
            try:
                projects = item.get_projects(*project_filter_criteria)
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
                projects = item.get_projects()
                reports = cls.get_reports_for_projects(
                    projects,
                    *time_criteria)
                indicator_sum = cls.sum_indicator_values(
                    indicator_key, reports)
                indicator_values.append(indicator_sum)
            except ReportError:
                indicator_values.append(0)

        return indicator_values

    @classmethod
    def get_trend_values_for_performance_indicators(cls,
                                                    collection,
                                                    indicator_key,
                                                    indicator_type,
                                                    **kwargs):
        project_filter_criteria = kwargs.get('project_criteria', [])
        time_criteria = kwargs.get('time_criteria', [])
        indicator_values = []
        for item in collection:
            try:

                projects = item.get_projects(*project_filter_criteria)
                reports = cls.get_reports_for_projects(
                    projects,
                    *time_criteria)
                try:
                    indicator_sum = (
                        cls.sum_performance_indicator_values(
                            indicator_key, indicator_type, reports))
                    indicator_values.append(indicator_sum)
                except ValueError:
                    indicator_values.append(0)

            except ReportError:
                indicator_values.append(0)

        return indicator_values


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


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
    def get_year_periods(cls):
        results = DBSession.query(Report)\
            .distinct(Report.period)\
            .order_by(Report.period)\
            .all()
        year_periods = [r.period for r in results]
        return year_periods

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
            projects = item.get_projects()

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
                                        **kwargs):
        """
        Generate performance indicators for a given sector whose values are
        determined from the provided set of indicators
        """
        rows = []
        sector_projects = []
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

                # populate project's list for rendering on map
                sector_projects.extend(projects)

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

        return rows, summary_row, sector_projects


class ReportError(Exception):
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

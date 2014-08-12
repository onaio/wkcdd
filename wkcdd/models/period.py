from sqlalchemy import desc, and_
from wkcdd.models import Report, Project
from wkcdd.models.base import DBSession


class Period(object):
    quarter = None
    year = None

    def __init__(self, quarter, year):
        self.quarter = quarter
        self.year = year

    def __bool__(self):
        return bool(self.quarter and self.year)

    @classmethod
    def latest_quarter(cls):
        result = DBSession.query(Report.quarter, Report.period)\
            .filter(Report.status == Report.APPROVED)\
            .group_by(Report.quarter, Report.period)\
            .order_by(desc(Report.quarter))\
            .first()

        return Period(result[0], result[1])

    @classmethod
    def get_periods_for_project(cls, project):
        results = DBSession.query(Report.quarter, Report.period)\
            .filter(and_(
                Project.code == project.code,
                Report.project_code == Project.code))\
            .group_by(Report.quarter, Report.period)\
            .order_by(Report.period, Report.quarter).all()

        periods = []
        for quarter, year in results:
            periods.append(Period(quarter=quarter, year=year))

        return periods

    @classmethod
    def get_periods_available(cls):
        results = DBSession.query(Report.quarter, Report.period)\
            .filter(Report.project_code == Project.code)\
            .group_by(Report.quarter, Report.period)\
            .order_by(Report.period, Report.quarter).all()

        periods = []
        for quarter, year in results:
            periods.append(Period(quarter=quarter, year=year))

        return periods

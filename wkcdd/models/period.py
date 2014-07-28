from sqlalchemy import desc
from wkcdd.models import Report
from wkcdd.models.base import DBSession


class Period(object):
    quarter = None
    year = None

    def __init__(self, quarter, year):
        self.quarter = quarter
        self.year = year

    def __bool__(self):
        return self.quarter and self.year

    @classmethod
    def latest_quarter(cls):
        result = DBSession.query(Report.quarter, Report.period)\
            .filter(Report.status == Report.APPROVED)\
            .group_by(Report.quarter, Report.period)\
            .order_by(desc(Report.quarter))\
            .first()

        return Period(result[0], result[1])

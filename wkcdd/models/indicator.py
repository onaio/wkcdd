from sqlalchemy import Float
from sqlalchemy.sql import func

from wkcdd import constants
from wkcdd.models import Report, Project
from wkcdd.models.base import DBSession


class Indicator(object):
    indicator_list = []

    @classmethod
    def sum_indicator_query(cls, project_ids, indicator):
        query = DBSession.query(
            func.sum(
                Report.report_data[indicator].cast(Float)))\
            .join(Project, Report.project_code == Project.code)\
            .filter(Project.id.in_(project_ids))\
            .filter(Report.status == Report.APPROVED)
        return query.first()[0]

    @classmethod
    def get_value(cls, project_ids):
        total = 0

        for indicator in cls.indicator_list:
            value = cls.sum_indicator_query(project_ids, indicator)

            if value:
                total += value

        return total


class TotalDirectBeneficiariesIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATOR_DIRECT_BENEFICIARIES

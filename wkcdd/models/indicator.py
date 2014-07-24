from sqlalchemy import Float
from sqlalchemy.sql import func

from wkcdd import constants
from wkcdd.models import (
    Report,
    Project,
    MeetingReport)
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


class RatioIndicator(object):
    numerator_class = None
    denomenator_class = None

    def __init__(self, numerator, denomenator):
        self.numerator_class = numerator
        self.denomenator_class = denomenator

    @classmethod
    def get_value(cls, project_ids):
        numerator_value = cls.numerator_class.get_value(project_ids)
        denomenator_value = cls.denomenator_class.get_value(project_ids)

        if not denomenator_value:
            return 0

        return float(numerator_value) / float(denomenator_value)


class TotalDirectBeneficiariesIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATOR_DIRECT_BENEFICIARIES


class TotalAverageMonthlyIncomeIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATOR_AVERAGE_MONTHLY_INCOME


class TotalBeneficiariesIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATOR_TOTAL_BENEFICIARIES


class TotalFemaleBeneficiariesIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATORS_FEMALE_BENEFICIARIES


class TotalVulnerableCIGMemberIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATORS_VULN_MEMBERS


class TotalCIGMemberIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATORS_TOTAL_MEMBERS


class PercentageIncomeIncreasedIndicator(RatioIndicator):
    numerator_class = TotalAverageMonthlyIncomeIndicator
    denomenator_class = TotalDirectBeneficiariesIndicator


class MeetingReportIndicator(Indicator):
    @classmethod
    def sum_indicator_query(cls, quarter, indicator):
        query = DBSession.query(
            func.sum(
                MeetingReport.report_data[indicator].cast(Float)))\
            .filter(MeetingReport.quarter == quarter)
        return query.first()[0]


class ExpectedCGAAttendanceIndicator(MeetingReportIndicator):
    indicator_list = constants.RESULT_INDICATORS_CGA_EXPECTED_ATTENDANCE


class ActualCGAAttendanceIndicator(MeetingReportIndicator):
    indicator_list = constants.RESULT_INDICATORS_CGA_ACTUAL_ATTENDANCE


class PercentageCGAAttendanceIndicator(RatioIndicator):
    numerator_class = ExpectedCGAAttendanceIndicator
    denomenator_class = ActualCGAAttendanceIndicator


class ExpectedCDDCAttendanceIndicator(MeetingReportIndicator):
    indicator_list = constants.RESULT_INDICATORS_EXPECTED_CDDC_ATTENDANCE


class ActualCDDCAttendanceIndicator(MeetingReportIndicator):
    indicator_list = constants.RESULT_INDICATORS_ACTUAL_CDDC_ATTENDANCE


class PercentageCDDCAttendanceIndicator(RatioIndicator):
    numerator_class = ExpectedCDDCAttendanceIndicator
    denomenator_class = ActualCDDCAttendanceIndicator


class ExpectedPMCAttendanceIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATORS_EXPECTED_PMC_ATTENDANCE


class ActualPMCAttendanceIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATORS_ACTUAL_PMC_ATTENDANCE


class PercentagePMCAttendanceIndicator(RatioIndicator):
    numerator_class = ExpectedPMCAttendanceIndicator
    denomenator_class = ActualPMCAttendanceIndicator


class ExpectedCIGAttendanceIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATORS_EXPECTED_CIG_ATTENDANCE


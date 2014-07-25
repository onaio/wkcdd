from sqlalchemy import Float
from sqlalchemy.sql import func, and_

from wkcdd import constants
from wkcdd.models import (
    Report,
    Project,
    MeetingReport
    )
from wkcdd.models.base import DBSession
from wkcdd.models.period import Period


class Indicator(object):
    indicator_list = []

    @classmethod
    def _get_period_criteria(cls, period):
        quarter = period.quarter
        year = period.year
        criteria = and_(Report.quarter == quarter, Report.period == year)

        return criteria

    @classmethod
    def get_quarter_criteria_list(cls, quarters):
        quarter_criteria_list = []

        if isinstance(quarters, list):
            for period in quarters:
                quarter_criteria_list.append(cls._get_period_criteria(period))
        else:
            quarter_criteria_list.append(cls._get_period_criteria(quarters))

        return quarter_criteria_list

    @classmethod
    def sum_indicator_query(cls, project_ids, indicator, quarters):
        quarter_criteria_list = cls.get_quarter_criteria_list(quarters)

        query = DBSession.query(
            func.sum(
                Report.report_data[indicator].cast(Float)))\
            .join(Project, Report.project_code == Project.code)\
            .filter(Project.id.in_(project_ids))\
            .filter(*quarter_criteria_list)\
            .filter(Report.status == Report.APPROVED)

        return query.first()[0]

    @classmethod
    def get_value(cls, project_ids, quarters):
        total = 0

        for indicator in cls.indicator_list:
            value = cls.sum_indicator_query(project_ids, indicator, quarters)

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
    def get_value(cls, project_ids, quarters):
        numerator_value = cls.numerator_class.get_value(
            project_ids, quarters)
        denomenator_value = cls.denomenator_class.get_value(
            project_ids, quarters)

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
    def sum_indicator_query(cls, quarters, indicator):

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


class ActualCIGAttendanceIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATORS_ACTUAL_CIG_ATTENDANCE


class PercentageCIGAttendanceIndicator(RatioIndicator):
    numerator_class = ExpectedCIGAttendanceIndicator
    denomenator_class = ActualCIGAttendanceIndicator


class CountIndicator(object):
    klass = None
    fields = []
    count_criteria = []

    @classmethod
    def count_indicator_query(cls, quarter):
        and_criteria = []
        for idx, field in enumerate(cls.fields):
            and_criteria.append(
                cls.klass.report_data[field].cast(Float) >=
                cls.count_criteria[idx])

        query = DBSession.query(MeetingReport)\
            .filter(MeetingReport.quarter == quarter)\
            .filter(and_(*and_criteria))

        return query.count()

    @classmethod
    def get_value(cls, quarters):
        return cls.count_indicator_query(quarters)


class CDDCManagemnentCountIndicator(CountIndicator):
    klass = MeetingReport
    fields = constants.RESULT_INDICATORS_CDDC_MANAGEMENT_COUNT
    count_criteria = [50.0, 50.0]


class ProjectMappingIndicator(CountIndicator):
    @classmethod
    def count_indicator_query(cls):
        query = DBSession.query(Project).filter(Project.geolocation != None)
        return query.count()

    @classmethod
    def get_value(cls):
        return cls.count_indicator_query()


class FinancialInformationIndicator(CountIndicator):
    klass = Report

    @classmethod
    def count_indicator_query(cls, project_ids):
        financial_info = constants.RESULT_INDICATORS_ACTUAL_CONTRIBUTION
        query = DBSession.query(Report)\
            .join(Project, Report.project_code == Project.code)\
            .filter(Project.id.in_(project_ids))\
            .filter(Report.report_data[financial_info].cast(Float) != None)
        return query.count()

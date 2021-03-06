from sqlalchemy import Float, null
from sqlalchemy.sql import func, and_

from wkcdd import constants
from wkcdd.models import (
    Report,
    Project,
    MeetingReport,
    SaicMeetingReport)
from wkcdd.models.helpers import get_sub_counties_list
from wkcdd.models.base import DBSession


class Indicator(object):
    klass = Report
    indicator_list = []

    @classmethod
    def _get_period_criteria(cls, period):
        quarter = period.quarter
        year = period.year
        criteria = and_(cls.klass.quarter == quarter, cls.klass.period == year)

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
    def count_indicator_query(cls, quarters):
        quarter_criteria_list = cls.get_quarter_criteria_list(quarters)
        and_criteria = []
        for idx, field in enumerate(cls.fields):
            and_criteria.append(
                cls.klass.report_data[field].cast(Float) >=
                cls.count_criteria[idx])

        query = DBSession.query(cls.klass)\
            .filter(*quarter_criteria_list)\
            .filter(and_(*and_criteria))

        return query.count()

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


class MeetingReportIndicator(Indicator):

    @classmethod
    def _get_period_criteria(cls, period):
        quarter = period.quarter
        year = period.year
        criteria = and_(MeetingReport.quarter == quarter,
                        MeetingReport.period == year)

        return criteria

    @classmethod
    def sum_indicator_query(cls, indicator, quarters):
        quarter_criteria_list = cls.get_quarter_criteria_list(quarters)

        query = DBSession.query(
            func.sum(
                MeetingReport.report_data[indicator].cast(Float)))\
            .filter(*quarter_criteria_list)

        return query.first()[0]

    @classmethod
    def get_value(cls, quarters):
        total = 0
        for indicator in cls.indicator_list:
            value = cls.sum_indicator_query(indicator, quarters)

            if value:
                total += value

        return total


class CountIndicator(Indicator):
    klass = None
    fields = []
    count_criteria = []

    @classmethod
    def get_value(cls, quarters):
        return cls.count_indicator_query(quarters)


class MeetingReportRatioIndicator(RatioIndicator):
    @classmethod
    def get_value(cls, quarters):
        numerator_value = cls.numerator_class.get_value(quarters)
        denomenator_value = cls.denomenator_class.get_value(quarters)

        if not denomenator_value:
            return 0

        return float(numerator_value) / float(denomenator_value)


class CDDCManagementCountIndicator(CountIndicator):
    DESCRIPTION = "Number of CDDCs managing development priorities \
identified in the CAPs and YAPs"
    klass = MeetingReport
    fields = constants.RESULT_INDICATORS_CDDC_MANAGEMENT_COUNT
    count_criteria = [50.0, 50.0]


class InitialAverageMonthlyIncomeIndicator(Indicator):

    @classmethod
    def get_value(cls, project_ids, quarters):
        intial_monthly_average_income = {
            'bondo': 6167.16,
            'bungoma': 1758.00,
            'busia': 2730.54,
            'butere': 2425.66,
            'kakamega': 6490.00,
            'lugari': 2555.60,
            'mt_elgon': 2357.00,
            'siaya': 152.81,
            'teso': 416.00,
            'vihiga': 5511.00
        }

        sub_counties = get_sub_counties_list(project_ids)
        value = 0

        for sub_county in sub_counties:
            value += intial_monthly_average_income[sub_county.name.lower()]

        return value


class CurrentTotalAverageMonthlyIncomeIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATOR_AVERAGE_MONTHLY_INCOME


class TotalBeneficiariesIndicator(Indicator):
    DESCRIPTION = "Total number of people in the project target area \
benefiting from project interventions (of which at least \
34% are female)"
    indicator_list = constants.RESULT_INDICATOR_TOTAL_BENEFICIARIES


class TotalFemaleBeneficiariesIndicator(Indicator):
    DESCRIPTION = "Proportion of female benefiting from project interventions"
    indicator_list = constants.RESULT_INDICATORS_FEMALE_BENEFICIARIES


class TotalVulnerableCIGMemberIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATORS_VULN_MEMBERS


class TotalCIGMemberIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATORS_TOTAL_MEMBERS


class CIGMemberRatioIndicator(RatioIndicator):
    DESCRIPTION = "Proportion of the most vulnerable community members \
participating in implementation of the project"

    numerator_class = TotalVulnerableCIGMemberIndicator
    denomenator_class = TotalCIGMemberIndicator


class TotalAverageMonthlyIncomeIndicator(RatioIndicator):
    numerator_class = CurrentTotalAverageMonthlyIncomeIndicator
    denomenator_class = TotalCIGMemberIndicator


class PercentageIncomeIncreasedIndicator(RatioIndicator):
    DESCRIPTION = "Percentage increase in income of target households \
members of CIGs (Direct beneficiaries)"

    numerator_class = TotalAverageMonthlyIncomeIndicator
    denomenator_class = InitialAverageMonthlyIncomeIndicator


class ExpectedCGAAttendanceIndicator(MeetingReportIndicator):
    indicator_list = constants.RESULT_INDICATORS_CGA_EXPECTED_ATTENDANCE


class ActualCGAAttendanceIndicator(MeetingReportIndicator):
    indicator_list = constants.RESULT_INDICATORS_CGA_ACTUAL_ATTENDANCE


class CGAAttendanceRatioIndicator(MeetingReportRatioIndicator):
    DESCRIPTION = "Percent of community members participating in \
Community General Meetings"

    numerator_class = ExpectedCGAAttendanceIndicator
    denomenator_class = ActualCGAAttendanceIndicator


class ExpectedCDDCAttendanceIndicator(MeetingReportIndicator):
    indicator_list = constants.RESULT_INDICATORS_EXPECTED_CDDC_ATTENDANCE


class ActualCDDCAttendanceIndicator(MeetingReportIndicator):
    indicator_list = constants.RESULT_INDICATORS_ACTUAL_CDDC_ATTENDANCE


class CDDCAttendanceRatioIndicator(MeetingReportRatioIndicator):
    DESCRIPTION = "Percent of CDDC members participating in decision making"
    numerator_class = ExpectedCDDCAttendanceIndicator
    denomenator_class = ActualCDDCAttendanceIndicator


class ExpectedPMCAttendanceIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATORS_EXPECTED_PMC_ATTENDANCE


class ActualPMCAttendanceIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATORS_ACTUAL_PMC_ATTENDANCE


class PMCAttendanceRatioIndicator(RatioIndicator):
    DESCRIPTION = "Percent of PMC members participating in decision making"
    numerator_class = ExpectedPMCAttendanceIndicator
    denomenator_class = ActualPMCAttendanceIndicator


class ExpectedCIGAttendanceIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATORS_EXPECTED_CIG_ATTENDANCE


class ActualCIGAttendanceIndicator(Indicator):
    indicator_list = constants.RESULT_INDICATORS_ACTUAL_CIG_ATTENDANCE


class CIGAttendanceRatioIndicator(RatioIndicator):
    DESCRIPTION = "Percent of CIG members participating in decision making"
    numerator_class = ExpectedCIGAttendanceIndicator
    denomenator_class = ActualCIGAttendanceIndicator


class ProjectInformationIndicator(Indicator):
    @classmethod
    def count_indicator_query(cls, project_ids, quarters):
        query = DBSession.query(Report)\
            .join(Project, Report.project_code == Project.code)\
            .filter(Project.id.in_(project_ids))\
            .filter(Project.geolocation != null())
        return query.count()

    @classmethod
    def get_value(cls, project_ids, quarters):
        return cls.count_indicator_query(project_ids, quarters)


class TotalProjectCountIndicator(object):
    @classmethod
    def get_value(cls, quarters):
        return Project.count()


class UpdatedProjectRatioIndicator(RatioIndicator):
    DESCRIPTION = "Percentage of sub projects including financial \
information updated and disclosed on mapping platform"

    numerator_class = ProjectInformationIndicator
    denomenator_class = TotalProjectCountIndicator

    @classmethod
    def get_value(cls, project_ids, quarters):
        numerator_value = cls.numerator_class.get_value(project_ids, quarters)
        denomenator_value = cls.denomenator_class.get_value(quarters)

        if not denomenator_value:
            return 0

        return float(numerator_value) / float(denomenator_value)


class SaicComplaintsReceivedIndicator(MeetingReportIndicator):
    indicator_list = SaicMeetingReport.COMPLAINTS_RECEIVED


class SaicComplaintsResolvedIndicator(MeetingReportIndicator):
    indicator_list = SaicMeetingReport.COMPLAINTS_RESOLVED


class SaicComplaintsResolveRatioIndicator(MeetingReportRatioIndicator):
    DESCRIPTION = "Proportion of complaints resolved"
    numerator_class = SaicComplaintsResolvedIndicator
    denomenator_class = SaicComplaintsReceivedIndicator


class SaicExpectedMeetingIndicator(MeetingReportIndicator):
    indicator_list = SaicMeetingReport.EXPECTED_MEETINGS


class SaicActualMeetingIndicator(MeetingReportIndicator):
    indicator_list = SaicMeetingReport.ACTUAL_MEETINGS


class SaicMeetingRatioIndicator(MeetingReportRatioIndicator):
    DESCRIPTION = "Proportion of meetings conducted by Social Audit \
Committees at the community level"

    numerator_class = SaicActualMeetingIndicator
    denomenator_class = SaicExpectedMeetingIndicator

from wkcdd import constants

from wkcdd.models.base import (
    Base,
    DBSession
)
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String
)
from sqlalchemy.dialects.postgresql import JSON


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
            impact_indicators[key] = cls.report_data[impact_indicator_key]
        return impact_indicators

    def calculate_performance_indicators(cls):
        performance_indicators = {}
        for key, performance_indicator_key\
            in constants.PERFORMANCE_INDICATORS[cls.report_data[
                constants.XFORM_ID]]:
            performance_indicators[key] = cls.\
                report_data[performance_indicator_key]
        return performance_indicators

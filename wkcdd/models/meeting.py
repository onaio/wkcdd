
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String)

from sqlalchemy.dialects.postgresql import JSON
from wkcdd.models.base import Base


class MeetingReport(Base):
    __tablename__ = 'meeting_reports'

    id = Column(Integer, primary_key=True, nullable=False)
    month = Column(Integer, nullable=False)
    quarter = Column(String, nullable=False)
    period = Column(String, nullable=False)
    submission_time = Column(DateTime(timezone=True), nullable=False)

    report_form_id = Column(String, nullable=False)
    report_data = Column(JSON, nullable=False)

    __mapper_args__ = {
        'polymorphic_on': report_form_id,
        'polymorphic_identity': 'meeting_report'
    }


class SaicMeetingReport(MeetingReport):
    FORM_ID = 'saic_meetings_complaints_status_report'
    REPORT_MONTH = 'summary/month'
    REPORT_QUARTER = 'summary/quarter_year'
    REPORT_PERIOD = 'summary/year'

    COMPLAINTS_RECEIVED = 'complain_status/saic_complains_recieved'
    COMPLAINTS_RESOLVED = 'complain_status/saic_complains_resolved'

    EXPECTED_MEETINGS = 'status_saic/saic_em'
    ACTUAL_MEETINGS = 'status_saic/saic_mh'

    __mapper_args__ = {
        'polymorphic_identity': 'saic_meeting_report'
    }

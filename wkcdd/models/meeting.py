
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

    report_data = Column(JSON, nullable=False)

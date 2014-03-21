from wkcdd.models.base import (
    Base,
    DBSession
)
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
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
        DBSession.add(report)

    @classmethod
    def calculate_indicators(cls):
        pass

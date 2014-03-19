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
    project_id = Column(String,
                        ForeignKey('projects.project_code'),
                        nullable=False)
    report_date = Column(DateTime(timezone=True), nullable=False)
    report_data = Column(JSON, nullable=False)
    form_id = Column(String, ForeignKey('forms.form_id'), nullable=False)

    @classmethod
    def add_report_submission(cls, report):
        DBSession.add(report)

    @classmethod
    def calculate_indicators(cls):
        pass

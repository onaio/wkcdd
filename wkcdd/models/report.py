from wkcdd.models.base import Base
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import JSON


class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True, nullable=False)
    project_id = Column(Integer, ForeignKey('location_types.id'), nullable=False)
    report_date = Column(DateTime(timezone=True), nullable=False)
    report_data = Column(JSON, nullable=False)

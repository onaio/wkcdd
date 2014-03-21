from wkcdd import constants
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
from sqlalchemy.sql import select


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

    def calculate_impact_indicators(cls):
        report_table = Base.metadata.tables['reports']

        return DBSession.execute(
                select(["report_data->>\
                       'impact_information/b_income' as\
                       no_of_b_increased_income",
                       "report_data->>\
                       'impact_information/b_improved_houses' as\
                       no_of_b_improved_houses",
                       "report_data->>\
                       'impact_information/b_hh_assets' as\
                       no_of_b_hh_assets",
                       "report_data->>\
                       'impact_information/no_children' as\
                        no_of_children"]
                    )
                .select_from(report_table)
                .where(
                    report_table.c.id == cls.id
                )).fetchone()

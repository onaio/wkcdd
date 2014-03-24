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
from sqlalchemy.sql import select


class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True, nullable=False)
    report_type = Column(String, nullable=False)
    project_code = Column(String, nullable=False, index=True)
    submission_time = Column(DateTime(timezone=True), nullable=False)
    month = Column(Integer, nullable=False)
    quarter = Column(String, nullable=False)
    period = Column(String, nullable=False)
    report_data = Column(JSON, nullable=False)
    # impact indicator fields
    no_of_b_increased_income = Column(Integer, nullable=False, default=0)
    no_of_b_improved_houses = Column(Integer, nullable=False, default=0)
    no_of_b_hh_assets = Column(Integer, nullable=False, default=0)
    no_of_children = Column(Integer, nullable=False, default=0)
    # common performance indicators
    expected_tot_contribution = Column(Integer, nullable=False, default=0)
    actual_tot_contribution = Column(Integer, nullable=False, default=0)
    direct_ben_achievement = Column(Integer, nullable=False, default=0)
    male_ben_achievement = Column(Integer, nullable=False, default=0)
    female_ben_achievement = Column(Integer, nullable=False, default=0)
    vulnerable_ben_achievement = Column(Integer, nullable=False, default=0)

    __mapper_args__ = {
      'polymorphic_identity': 'report',
      'polymorphic_on': report_type
    }

    @classmethod
    def add_report_submission(cls, report):
        DBSession.add(report)

    def calculate_impact_indicators(cls):
        return_fields = ["report_data->>\
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
        return query(return_fields)

    # def calculate_performance_indicators(cls):
    #   return_fields = ["report_data->>\
    #        'perfomance_summary/exp_contribution' as\
    #         no_of_b_increased_income",
    #                      "report_data->>\
    #        'impact_information/b_improved_houses' as\
    #        no_of_b_improved_houses",
    #                      "report_data->>\
    #        'impact_information/b_hh_assets' as\
    #        no_of_b_hh_assets",
    #                      "report_data->>\
    #        'impact_information/no_children' as\
    #         no_of_children"]   

    def query(cls, return_fields):
      report_table = Base.metadata.tables['reports']
      return DBSession.execute(
            select(return_fields)
            .select_from(report_table)
            .where(
                report_table.c.id == cls.id
            )).fetchone()

class BodaBodaReport(Report):
  
  __mapper_args__ = {
      'polymorphic_identity':'boda_boda_report'
  }



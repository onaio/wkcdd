from sqlalchemy.dialects.postgresql import JSON
from wkcdd.models.base import DBSession
from wkcdd.models.base import Base
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Integer
)


class Form(Base):
    __tablename__ = 'forms'
    form_id = Column(String, primary_key=True, nullable=False)
    form_name = Column(String, nullable=False)
    project_type_id = Column(Integer, ForeignKey('project_type.id'), nullable=False)
    form_type_id = Column(Integer, ForeignKey('form_types.id'), nullable=False)
    form_data = Column(JSON, nullable=False)

    @classmethod
    def get_registration_form_id(cls):
        registration_form = DBSession.query(Form).join(FormTypes).filter(
            FormTypes.name == 'registration').first()
        return registration_form.form_id

    @classmethod
    def get_report_form_id(cls):
        registration_form = DBSession.query(Form).join(FormTypes).filter(
            FormTypes.name == 'report').first()
        return registration_form.form_id


class FormTypes(Base):
    __tablename__ = 'form_types'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String,nullable=False)
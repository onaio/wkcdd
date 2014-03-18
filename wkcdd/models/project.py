from wkcdd.models.base import Base
from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    ForeignKey
)


class Project(Base):
    __tablename__ = 'projects'
    project_code = Column(String, primary_key=True, autoincrement=False, nullable=False)
    name = Column(Text, nullable=False, nullable=False)
    community_id = Column(Integer, ForeignKey('communities.id'), nullable=False)

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
    project_code = Column(String, primary_key=True, autoincrement=False,
                          nullable=False)
    name = Column(Text, nullable=False)
    community_id = Column(Integer, ForeignKey('communities.id'),
                          nullable=False)
    project_type_id = Column(Integer, ForeignKey('project_type.id'),
                             nullable=False)

    def get_registered_projects(self, ):
        pass


class ProjectType(Base):
    __tablename__ = 'project_type'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)

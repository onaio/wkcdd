from wkcdd.models.base import Base
from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    ForeignKey
)
from sqlalchemy.orm.exc import NoResultFound


class Project(Base):
    __tablename__ = 'projects'
    code = Column(String, primary_key=True, autoincrement=False,
                          nullable=False)
    name = Column(Text, nullable=False)
    community_id = Column(Integer, ForeignKey('communities.id'),
                          nullable=False)
    project_type_id = Column(Integer, ForeignKey('project_type.id'),

                             nullable=False)
    @classmethod
    def create(self, **kwargs):
        project = Project(code=kwargs['project_code'],
                          name=kwargs['name'],
                          community_id=kwargs['community_id'],
                          project_type_id=kwargs['project_type_id']
        )
        project.save()

    def get_registered_projects(self):
        pass


class ProjectType(Base):
    __tablename__ = 'project_type'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)

    @classmethod
    def get_or_create(cls, name):
         # check if exists
        try:
            project_type = ProjectType.get(ProjectType.name == name)
        except NoResultFound:
            project_type = ProjectType(name=name)
            project_type.save()

        return project_type

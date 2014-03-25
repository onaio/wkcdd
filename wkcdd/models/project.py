from wkcdd.models.base import Base
from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    ForeignKey
)

from sqlalchemy.orm import (
    relationship,
    backref
)
from sqlalchemy.orm.exc import NoResultFound

from wkcdd.models import (
    Community,
    Location)


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False, index=True)
    name = Column(Text, nullable=False)
    community_id = Column(Integer, ForeignKey('communities.id'),
                          nullable=False)
    community = relationship("Community",
                             backref=backref('communities', order_by=id))
    project_type_id = Column(Integer, ForeignKey('project_type.id'),
                             nullable=False)
    project_type = relationship("ProjectType",
                                backref=backref('project_types', order_by=id))
    reports = relationship("Report",
                           backref=backref('project', order_by=id),
                           primaryjoin="Project.code == \
                           foreign(Report.project_code)")

    @classmethod
    def create(self, **kwargs):
        constituency = Location.get_or_create(
            kwargs['constituency'], 'constituency')
        community = Community.get_or_create(
            kwargs['community_name'], constituency, kwargs['geolocation']
        )
        project_type = ProjectType.get_or_create(kwargs['project_type'])

        project = Project(code=kwargs['project_code'],
                          name=kwargs['name'],
                          community_id=community.id,
                          project_type_id=project_type.id)
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

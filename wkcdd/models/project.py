from wkcdd import constants
from wkcdd.models.base import Base, BaseModelFactory
from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    ForeignKey
)

from sqlalchemy.orm import (
    relationship,
    backref,
    scoped_session,
    sessionmaker
)
from sqlalchemy.orm.exc import NoResultFound
from zope.sqlalchemy import ZopeTransactionExtension
from wkcdd.models import (
    Community,
    Location)

from wkcdd.models.county import County
from wkcdd.models.sub_county import SubCounty
from wkcdd.models.constituency import Constituency
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False, index=True)
    name = Column(Text, nullable=False)
    community_id = Column(Integer, ForeignKey('locations.id'),
                          nullable=False)
    community = relationship("Community",
                             backref=backref('projects', order_by=id),
                             primaryjoin="and_(\
                                Project.community_id == Location.id, \
                                Location.location_type =='community')")
    project_type_id = Column(Integer, ForeignKey('project_type.id'),
                             nullable=False)
    sector = Column(String, nullable=False)
    # TODO Possibly use postgis for geolocation
    geolocation = Column(Text, nullable=True)
    project_type = relationship("ProjectType",
                                backref=backref('project_types', order_by=id))
    reports = relationship("Report",
                           backref=backref('project', order_by=id),
                           primaryjoin="Project.code == \
                           foreign(Report.project_code)",
                           order_by='desc(Report.submission_time)')

    @classmethod
    def create(self, **kwargs):
        county = County.get_or_create(
            kwargs['county'], None, Location.COUNTY)
        sub_county = SubCounty.get_or_create(
            kwargs['sub_county'], county, Location.SUB_COUNTY)
        constituency = Constituency.get_or_create(
            kwargs['constituency'], sub_county, Location.CONSTITUENCY)
        community = Community.get_or_create(
            kwargs['community_name'], constituency, Location.COMMUNITY)
        project_type = ProjectType.get_or_create(kwargs['project_type'])

        project = Project(code=kwargs['project_code'],
                          name=kwargs['name'],
                          community_id=community.id,
                          project_type_id=project_type.id,
                          sector=kwargs['sector'],
                          geolocation=kwargs['geolocation'])
        project.save()

    @classmethod
    def get_constituency(cls, community):
        constituency_id = community.parent_id
        return Location.get(Location.id == constituency_id)

    @classmethod
    def get_sub_county(cls, constituency):
        sub_county_id = constituency.parent_id
        return Location.get(Location.id == sub_county_id)

    @classmethod
    def get_county(cls, sub_county):
        county_id = sub_county.parent_id
        return Location.get(Location.id == county_id)

    @classmethod
    def get_locations(cls, projects):
        locations = {}
        for project in projects:
            constituency = project.get_constituency(project.community)
            sub_county = project.get_sub_county(constituency)
            county = project.get_county(sub_county)
            locations[project.id] = [county, sub_county, constituency]

        return locations

    def get_latest_report(self):
        if self.reports:
            return self.reports[0]
        else:
            return None

    @classmethod
    def get_filter_criteria(cls):
        filter_criteria = {
            'sectors': constants.PROJECT_SECTORS,
            'counties': County.all(),
            'sub_counties': SubCounty.all(),
            'communities': Community.all(),
        }

        return filter_criteria


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


class ProjectFactory(BaseModelFactory):
    __acl__ = []

    def __getitem__(self, item):
        # try to retrieve the project whose id matches item
        try:
            project_id = int(item)
            project = DBSession.query(Project).filter_by(id=project_id).one()
        except (ValueError, NoResultFound):
            raise KeyError
        else:
            project.__parent__ = self
            project.__name__ = item
            return project

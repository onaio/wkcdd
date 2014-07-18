import warnings
import json

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
from sqlalchemy.dialects.postgresql import JSON

from zope.sqlalchemy import ZopeTransactionExtension

from wkcdd.libs.utils import humanize
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
    # TODO index sector field
    sector = Column(String, nullable=False, index=True)
    # TODO Possibly use postgis for geolocation
    geolocation = Column(Text, nullable=True)
    project_type = relationship("ProjectType",
                                backref=backref('project_types', order_by=id))
    reports = relationship("Report",
                           backref=backref('project', order_by=id),
                           primaryjoin="Project.code == \
                           foreign(Report.project_code)",
                           order_by='desc(Report.submission_time)')
    project_data = Column(JSON, nullable=False)

    def __str__(self):
        return self.name

    @property
    def pretty(self):
        return humanize(self.name).title()

    @property
    def latlong(self):
        latlong = []
        if self.geolocation and self.geolocation.strip():
            latlong = self.geolocation.split(' ')[0:2]
            latlong = latlong if latlong[0] and latlong[1] else []

        return latlong

    @property
    def sector_name(self):
        sectors_dict = {
            reg_id: label
            for reg_id, report_id, label in constants.PROJECT_TYPE_MAPPING}
        return sectors_dict[self.sector]

    @property
    def description(self):
        description_list = [(label, self.project_data.get(key).title())
                            for key, label in constants.PROJECT_DETAILS_KEYS]
        return description_list

    @property
    def image_file(self):
        return self.project_data.get('group_photo') or ''

    def get_projects(self, *criterion):
        if criterion is not None:
            try:
                project = Project.get(Project.id == self.id, *criterion)
                return [project]
            except NoResultFound:
                return None

        else:
            return [self]

    def get_project_ids(self, *criterion):
        if criterion is not None:
            try:
                project = Project.get(Project.id == self.id, *criterion)
                return [project.id]
            except NoResultFound:
                return None

        else:
            return [self.id]

    def url(self, request, route_name, query_params=None):
        return request.route_url(
            'projects', traverse=(self.id), _query=query_params)

    @classmethod
    def create(cls, **kwargs):
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
                          geolocation=kwargs['geolocation'],
                          project_data=kwargs['project_data'])
        project.save()

    @classmethod
    def get_constituency(cls, community):
        warnings.warn(
            "Use the specific county, sub_county and constituency properties"
            " within each location type e.g. sub_county.county",
            DeprecationWarning)
        constituency_id = community.parent_id
        return Location.get(Location.id == constituency_id)

    @classmethod
    def get_sub_county(cls, constituency):
        warnings.warn(
            "Use the specific county, sub_county and constituency properties"
            " within each location type e.g. sub_county.county",
            DeprecationWarning)
        sub_county_id = constituency.parent_id
        return Location.get(Location.id == sub_county_id)

    @classmethod
    def get_county(cls, sub_county):
        warnings.warn(
            "Use the specific county, sub_county and constituency properties"
            " within each location type e.g. sub_county.county",
            DeprecationWarning)
        county_id = sub_county.parent_id
        return Location.get(Location.id == county_id)

    @classmethod
    def get_locations(cls, projects):
        warnings.warn(
            "Use the specific county, sub_county and constituency properties"
            " within each location type e.g. sub_county.county",
            DeprecationWarning)
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
    def generate_filter_criteria(cls):
        sector_filter = [
            (reg_id, label)
            for reg_id, report_id, label in constants.PROJECT_TYPE_MAPPING]
        counties = County.all()
        sub_counties = SubCounty.all()
        constituencies = Constituency.all()
        communities = Community.all()
        location_json_data = [
            {
                "community": {
                    "name": community.pretty,
                    "id": community.id},
                "constituency": {
                    "name": community.constituency.pretty,
                    "id": community.constituency.id},
                "sub_county": {
                    "name": community.constituency.sub_county.pretty,
                    "id": community.constituency.sub_county.id},
                "county": {
                    "name": community.constituency.sub_county.county.pretty,
                    "id": community.constituency.sub_county.county.id}
            }
            for community in communities]
        filter_criteria = {
            'sectors': sector_filter,
            'counties': counties,
            'sub_counties': sub_counties,
            'constituencies': constituencies,
            'communities': communities,
            'location_json_data': json.dumps(location_json_data)
        }

        return filter_criteria

    @classmethod
    def get_rank(cls):
        return 5


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

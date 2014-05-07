from wkcdd.models.base import (
    Base,
    BaseModelFactory,
    DBSession
)

from sqlalchemy import (
    Column,
    Integer,
    Text,
    Enum,
    ForeignKey
)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import relationship

from wkcdd.libs.utils import humanize


class Location(Base):
    __tablename__ = 'locations'
    COUNTY = 'county'
    SUB_COUNTY = 'sub_county'
    CONSTITUENCY = 'constituency'
    COMMUNITY = 'community'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey('locations.id'), nullable=True)
    location_type = Column(Enum(COUNTY, SUB_COUNTY, CONSTITUENCY, COMMUNITY,
                           name='LOCATION_TYPES'),
                           nullable=False)
    parent = relationship("Location", remote_side=[id])

    __mapper_args__ = {
        'polymorphic_on': location_type,
        'polymorphic_identity': 'location'
    }

    def __str__(self):
        return self.name

    def children(self):
        return Location.all(Location.parent_id == self.id)

    @property
    def url(self):
        if self.location_type == self.COUNTY:
            return self.location_type[:-1] + 'ies'
        else:
            return self.location_type

    @classmethod
    def get_or_create(cls, name, parent, location_type):

        # get Location parent_id
        parent_id = parent.id if parent is not None else None

        try:
            location = Location.get(Location.name == name,
                                    Location.parent_id == parent_id,
                                    Location.location_type == location_type)
        except NoResultFound:
            location = Location(name=name,
                                parent_id=parent_id,
                                location_type=location_type)
            location.save()

        return location

    @classmethod
    def get_location_ids(cls, klass, parent_ids):
        """
        Get a list of location ids whose parent_id is in parent_ids
        """
        return DBSession\
            .query(klass.id)\
            .filter(cls.parent_id.in_(parent_ids))\
            .all()

    @property
    def pretty(self):
        """
        Return the humanized name of the location.
        """
        return humanize(self.name).title()

    @classmethod
    def get_child_ids(cls, parent_ids):
        raise NotImplementedError

    @classmethod
    def get_rank(cls):
        return 0


class LocationFactory(BaseModelFactory):
    __acl__ = []

    def __getitem__(self, item):
        # try to retrieve the project whose id matches item
        try:
            location_id = int(item)
            location = DBSession.query(Location).\
                filter_by(id=location_id).one()
        except (ValueError, NoResultFound):
            raise KeyError
        else:
            location.__parent__ = self
            location.__name__ = item
            return location

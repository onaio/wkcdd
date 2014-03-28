from wkcdd.models.base import Base
from sqlalchemy import (
    Column,
    Integer,
    Text,
    Enum
)
from sqlalchemy.orm.exc import NoResultFound


class Location(Base):
    __tablename__ = 'locations'
    COUNTY = 'county'
    SUB_COUNTY = 'sub_county'
    CONSTITUENCY = 'constituency'
    COMMUNITY = 'community'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    parent_id = Column(Integer, nullable=False)
    location_type = Column(Enum(COUNTY, SUB_COUNTY, CONSTITUENCY, COMMUNITY,
                           name='LOCATION_TYPES'),
                           nullable=False)

    __mapper_args__ = {
        'polymorphic_on': location_type,
        'polymorphic_identity': 'location'
    }

    @classmethod
    def get_or_create(cls, name, parent, location_type):

        # get Location parent_id
        parent_id = parent.id if parent is not None else 0

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

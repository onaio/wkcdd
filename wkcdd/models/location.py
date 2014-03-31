from wkcdd.models.base import Base
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey
)
from sqlalchemy.orm.exc import NoResultFound


class Location(Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    parent_id = Column(Integer, nullable=False)
    location_type = Column(Integer,
                           ForeignKey('location_types.id'),
                           nullable=False)

    @classmethod
    def get_or_create(cls, name, location_type, parent):

        location_type = LocationType.get_or_create(location_type)

        # get Location parent_id
        parent_id = parent.id if parent is not None else 0

        try:
            location = Location.get(Location.name == name,
                                    Location.parent_id == parent_id,
                                    Location.location_type == location_type.id)
        except NoResultFound:
            location = Location(name=name,
                                parent_id=parent_id,
                                location_type=location_type.id)
            location.save()

        return location


class LocationType(Base):
        __tablename__ = 'location_types'
        id = Column(Integer, primary_key=True, nullable=False)
        name = Column(Text, nullable=False)

        @classmethod
        def get_or_create(cls, name):
            try:
                location_type = LocationType.get(LocationType.name == name)
            except NoResultFound:
                location_type = LocationType(name=name)
                location_type.save()

            return location_type

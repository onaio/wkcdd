from wkcdd.models.base import Base
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey
)


class Location(Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    parent_id = Column(Integer, nullable=False)
    location_type = Column(Integer,
                           ForeignKey('location_types.id'),
                           nullable=False)

    @classmethod
    def get__or_create(cls, name, location_type):

        location_type = LocationType.get__or_create(location_type)
        #check if exists
        try:
            location = Location.get(name=name, location_type=location_type.id)
        except Exception:
            location = Location(name=name, location_type=location_type.id)
            location.save()

        return location


class LocationType(Base):
        __tablename__ = 'location_types'
        id = Column(Integer, primary_key=True, nullable=False)
        name = Column(Text, nullable=False)

        def get__or_create(cls, name):
            try:
                location_type = LocationType.get(name=name)
            except Exception:
                location_type = LocationType(name=name)
                LocationType.save()

            return location_type

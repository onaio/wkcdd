from wkcdd.models.base import Base
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey
)


class Locations(Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    parent_id = Column(Integer)
    location_type = Column(Integer, ForeignKey('location_types.id'))


class LocationType(Base):
        __tablename__ = 'location_types'
        id = Column(Integer, primary_key=True)
        name = Column(Text)
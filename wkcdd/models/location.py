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
    location_type = Column(Integer, ForeignKey('location_types.id'), nullable=False)


class LocationType(Base):
        __tablename__ = 'location_types'
        id = Column(Integer, primary_key=True, nullable=False)
        name = Column(Text, nullable=False)

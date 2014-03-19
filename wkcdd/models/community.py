from wkcdd.models.base import Base
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey
)


class Community(Base):
    __tablename__ = 'communities'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    constituency_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    geolocation = Column(Text, nullable=False)
    #TODO Possibly use postgis for geolocation

    @classmethod
    def get_or_create(cls, name, constituency, geolocation):
        # check if exists
        try:
            community = Community.get(name=name, constituency_id=constituency.id, geolocation=geolocation)
        except Exception:
            community = Community(name=name, constituency_id=constituency.id)
            community.save()
        # If not exist, create community
        # return community object
        return community

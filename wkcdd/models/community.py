from wkcdd.models.base import Base
from sqlalchemy import (
    Column,
    Integer,
    Text,
)


class Community(Base):
    __tablename__ = 'communities'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    constituency_id = Column(Integer)
    geolocation = Column(Text)

    #TODO Possibly use postgis for geolocation

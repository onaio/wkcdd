from wkcdd.models.base import Base
from sqlalchemy import (
    Column,
    Integer,
    Text,
)


class Community(Base):
    __tablename__ = 'communities'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    constituency_id = Column(Integer, nullable=False)
    geolocation = Column(Text, nullable=False)

    #TODO Possibly use postgis for geolocation

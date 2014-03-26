from wkcdd.models.base import Base

from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound


class Community(Base):
    __tablename__ = 'communities'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    constituency_id = Column(Integer, ForeignKey('locations.id'),
                             nullable=False)
    constituency = relationship("Location",
                                backref=backref('constituencies', order_by=id))

    @classmethod
    def get_or_create(cls, name, constituency):
        # check if exists
        try:
            community = Community.get(
                Community.name == name,
                Community.constituency_id == constituency.id)
        except NoResultFound:
            community = Community(name=name,
                                  constituency_id=constituency.id)
            community.save()
        # If not exist, create community
        # return community object
        return community

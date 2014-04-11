from wkcdd.models.base import DBSession
from sqlalchemy.sql.expression import and_

from wkcdd import constants
from wkcdd.models import (
    Location, Project)
from wkcdd.models.sub_county import SubCounty
from wkcdd.models.constituency import Constituency
from wkcdd.models.community import Community


def get_sub_county_ids(county_ids):
    return [sub_county.id for sub_county in
            Location.get_location_ids(SubCounty, county_ids)]


def get_constituency_ids(sub_county_ids):
    return [constituency.id for constituency in
            Location.get_location_ids(Constituency, sub_county_ids)]


def get_community_ids(constituency_ids):
    return [community.id for community in
            Location.get_location_ids(Community, constituency_ids)]


def get_project_list(community_ids, *criterion):
    return DBSession\
        .query(Project)\
        .filter(and_(Project.community_id.in_(community_ids),
                *criterion))\
        .all()


def get_project_types(community_ids, *criterion):
    registration_ids = [p.sector for p in
                        DBSession.query(Project.sector).filter(
                            and_(
                                Project.community_id.in_(community_ids),
                                *criterion)).group_by(Project.sector).all()]
    return [(reg_id, report_id, label)
            for reg_id, report_id, label in constants.PROJECT_TYPE_MAPPING
            if reg_id in registration_ids]

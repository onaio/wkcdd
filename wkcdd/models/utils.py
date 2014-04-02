from wkcdd.models.base import DBSession
from sqlalchemy.sql.expression import and_
from wkcdd.models import (
    Location, SubCounty, Constituency, Community, Project)


def get_sub_county_ids(county_ids):
    return [sub_county.id for sub_county in
            Location.get_location_ids(SubCounty, county_ids)]


def get_constituency_ids(sub_county_ids):
    return [constituency.id for constituency in
            Location.get_location_ids(Constituency, sub_county_ids)]


def get_community_ids(constituency_ids):
    return [community.id for community in
            Location.get_location_ids(Community, constituency_ids)]


def get_project_list(community_ids):
    return DBSession\
        .query(Project)\
        .filter(Project.community_id.in_(community_ids))\
        .all()


def get_project_list_by_sector(community_ids, sector):
    return DBSession\
        .query(Project)\
        .filter(and_(Project.community_id.in_(community_ids),
                Project.sector == sector))\
        .all()

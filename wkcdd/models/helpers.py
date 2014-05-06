from wkcdd.models.base import DBSession
from sqlalchemy.sql.expression import and_

from wkcdd import constants
from wkcdd.models import (
    Location, Project)
from wkcdd.models.sub_county import SubCounty
from wkcdd.models.constituency import Constituency
from wkcdd.models.community import Community
from wkcdd.models.county import County


def get_sub_county_ids(county_ids):
    return [] \
        if not county_ids else \
        [sub_county.id for sub_county in
            Location.get_location_ids(SubCounty, county_ids)]


def get_constituency_ids(sub_county_ids):
    return [] \
        if not sub_county_ids else \
        [constituency.id for constituency in
            Location.get_location_ids(Constituency, sub_county_ids)]


def get_community_ids(constituency_ids):
    return [] \
        if not constituency_ids else \
        [community.id for community in
            Location.get_location_ids(Community, constituency_ids)]


def get_project_list(community_ids, *criterion):
    return [] \
        if not community_ids else \
        DBSession.query(Project)\
        .filter(and_(Project.community_id.in_(community_ids),
                *criterion))\
        .all()


def get_project_ids(community_ids, *criterion):
    projects = DBSession.query(Project)\
        .filter(and_(Project.community_id.in_(community_ids),
                *criterion))\
        .all()
    return [] \
        if not community_ids else [p.id for p in projects]


def get_project_types(community_ids, *criterion):
    if community_ids:
        registration_ids = [p.sector for p in
                            DBSession.query(Project.sector).filter(
                                and_(
                                    Project.community_id.in_(community_ids),
                                    *criterion)).group_by(
                                Project.sector).all()]
        return [(reg_id, report_id, label)
                for reg_id, report_id, label in constants.PROJECT_TYPE_MAPPING
                if reg_id in registration_ids]
    else:
        return [(reg_id, report_id, label)
                for reg_id, report_id, label in constants.PROJECT_TYPE_MAPPING]


def get_community_ids_for(location_type, location_ids):
    community_ids = {
        Community: location_ids,
        Constituency: get_community_ids(location_ids),
        SubCounty: get_community_ids(get_constituency_ids
                                     (location_ids)),
        County: get_community_ids(get_constituency_ids
                                  (get_sub_county_ids
                                   (location_ids)))
    }[location_type]
    return community_ids


def get_children_by_level(location_ids, source_klass, target_klass):
    children_klass, child_ids = source_klass.get_child_ids(location_ids)
    if children_klass != target_klass:
        child_ids = get_children_by_level(
            child_ids, children_klass, target_klass)
    return child_ids

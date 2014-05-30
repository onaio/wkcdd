import re

from wkcdd.models.base import DBSession
from sqlalchemy.sql.expression import and_

from wkcdd import constants

from wkcdd.libs.utils import number_to_month_name

from wkcdd.models import (
    Location, Project)
from wkcdd.models.sub_county import SubCounty
from wkcdd.models.constituency import Constituency
from wkcdd.models.community import Community
from wkcdd.models.county import County
from wkcdd.models.report import Report


YEAR_PERIOD = 'period'
MONTH_PERIOD = 'month'
QUARTER_PERIOD = 'quarter'


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
    if source_klass.get_rank() < target_klass.get_rank():
        children_klass, child_ids = source_klass.get_child_ids(location_ids)
        if children_klass != target_klass:
            child_ids = get_children_by_level(
                child_ids, children_klass, target_klass)
        return child_ids
    else:
        raise ValueError(
            "Target class cannot be of a greater rank than the source class")


def get_period_row(time_series,
                   time_class,
                   item,
                   indicator_key,
                   **kwargs):
    period_row = []

    for period, year in time_series:
        period_label = None
        year_label = re.search('\d+', year).group(0)

        if time_class == YEAR_PERIOD:
            time_criteria = Report.period == period
            period_label = year_label

        elif time_class == MONTH_PERIOD:
            time_criteria = [Report.month == period,
                             Report.period == year]
            period_label = (
                number_to_month_name(period) +
                " {}".format(year_label))
        elif time_class == QUARTER_PERIOD:
            time_criteria = [Report.quarter == period,
                             Report.period == year]
            period_label = (period.replace("q_", "Quarter ") +
                            " {}".format(year_label))

        project_filter_criteria = kwargs.get('project_filter_criteria')
        if project_filter_criteria is not None:
            indicator_type = kwargs.get('indicator_type')

            criteria_args = {
                'project_filter_criteria': project_filter_criteria,
                'time_criteria': time_criteria}

            data = Report.get_trend_values_for_performance_indicators(
                [item], indicator_key, indicator_type, **criteria_args)
        else:
            data = Report.get_trend_values_for_impact_indicators(
                [item], indicator_key, *time_criteria)

        period_row.append([period_label, data[0]])

    return period_row

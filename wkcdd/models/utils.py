from wkcdd.models import Location, County, SubCounty, Constituency, Community


def get_sub_county_ids(parent_ids):
    return [sub_county.id for sub_county in
            Location.get_location_ids(SubCounty, parent_ids)]


def get_constituency_ids(parent_ids):
    return [constituency.id for constituency in
            Location.get_location_ids(Constituency, parent_ids)]


def get_community_ids(parent_ids):
    return [community.id for community in
            Location.get_location_ids(Community, parent_ids)]

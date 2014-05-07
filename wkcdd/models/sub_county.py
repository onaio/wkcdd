from wkcdd.models.location import Location


class SubCounty(Location):
    __mapper_args__ = {
        'polymorphic_identity': Location.SUB_COUNTY
    }

    def get_projects(self):
        """
        Get the list of projects associated with this county.
        """
        from wkcdd.models.helpers import (
            get_project_list, get_community_ids, get_constituency_ids)
        return get_project_list(
            get_community_ids(
                get_constituency_ids([self.id])))

    def is_found_in(self, location):
        return self.id == location.id or self.county.is_found_in(location)

    @property
    def county(self):
        return self.parent

    @county.setter
    def county(self, county):
        self.parent = county

    @classmethod
    def get_child_ids(cls, sub_county_ids):
        from helpers import get_constituency_ids
        return cls.get_child_class(), get_constituency_ids(sub_county_ids)

    @classmethod
    def get_child_class(cls):
        from constituency import Constituency
        return Constituency

    @classmethod
    def get_rank(cls):
        return 2

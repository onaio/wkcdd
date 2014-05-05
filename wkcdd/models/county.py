from wkcdd.models.location import Location


class County(Location):
    __mapper_args__ = {
        'polymorphic_identity': Location.COUNTY
    }

    def get_projects(self):
        """
        Get the list of projects associated with this county.
        """
        from wkcdd.models.helpers import (
            get_project_list, get_community_ids, get_constituency_ids,
            get_sub_county_ids)
        return get_project_list(
            get_community_ids(
                get_constituency_ids(
                    get_sub_county_ids([self.id]))))

    @classmethod
    def get_child_ids(cls, parent_ids):
        from helpers import get_sub_county_ids
        return cls.get_child_class(), get_sub_county_ids(parent_ids)

    @classmethod
    def get_child_class(cls):
        from sub_county import SubCounty
        return SubCounty
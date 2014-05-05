from wkcdd.models.location import Location


class County(Location):
    __mapper_args__ = {
        'polymorphic_identity': Location.COUNTY
    }

    def get_projects(self):
        from wkcdd.models.helpers import (
            get_project_list, get_community_ids, get_constituency_ids,
            get_sub_county_ids)
        return get_project_list(
            get_community_ids(
                get_constituency_ids(
                    get_sub_county_ids([self.id]))))
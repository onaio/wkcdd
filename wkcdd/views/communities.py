from pyramid.view import (
    view_defaults,
)


@view_defaults(route_name='projects')
class CommunitiesView(object):
    def list_all_communities(self):
        pass

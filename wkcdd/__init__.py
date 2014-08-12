from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config
from wkcdd.libs.utils import (
    format_percent,
    format_value,
    humanize
)

from jinja2.ext import with_
from wkcdd.security import group_finder, pwd_context

from wkcdd.models.base import (
    DBSession,
    Base)
from wkcdd.models.project import ProjectFactory
from wkcdd.models.location import LocationFactory
from wkcdd.models.report import ReportFactory
from wkcdd.models.user import UserFactory
from wkcdd.views.helpers import get_request_user


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    session_factory = UnencryptedCookieSessionFactoryConfig(
        settings['secret_key'])
    config = Configurator(settings=settings,
                          root_factory='wkcdd.models.base.RootFactory',
                          session_factory=session_factory)
    config.set_authentication_policy(
        AuthTktAuthenticationPolicy(settings['secret_key'],
                                    callback=group_finder,
                                    hashalg='sha512'))

    config.set_authorization_policy(ACLAuthorizationPolicy())

    # configure password context
    pwd_context.load_path(global_config['__file__'])

    includeme(config)
    return config.make_wsgi_app()


def includeme(config):
    config.include('pyramid_jinja2')
    # commit config to ensure config.get_jinja2_environment() is not None
    config.commit()
    config.add_jinja2_search_path("wkcdd:templates")
    config.add_jinja2_extension(with_, ".jinja2")
    config.get_jinja2_environment().filters['format_percent'] = format_percent
    config.get_jinja2_environment().filters['format_value'] = format_value
    config.get_jinja2_environment().filters['humanize'] = humanize

    # request methods
    config.add_request_method(get_request_user, 'user', reify=True)

    config.add_renderer('xlsx', 'wkcdd.renderers.TablibXLSXRenderer')
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('auth', '/auth/{action}')
    config.add_route('default', '/')
    config.add_route('projects', '/projects/*traverse',
                     factory=ProjectFactory)
    config.add_route('impact_indicators', '/impact-indicators/*traverse',
                     factory=LocationFactory)
    config.add_route('performance_indicators',
                     '/performance-indicators/*traverse',
                     factory=LocationFactory)
    config.add_route('results_indicators',
                     'results-indicators/*traverse',
                     factory=LocationFactory)
    config.add_route('reports', '/reports/*traverse',
                     factory=ReportFactory)
    config.add_route('users',
                     '/users/*traverse',
                     factory=UserFactory)

    config.add_route('exports', '/exports')
    config.add_route('export_projects', '/export-projects')
    config.add_route('export_reports', '/export-reports')

    config.add_route('reporting_status', '/reporting_status')
    config.add_route('private', '/private')
    config.add_route('supervisors_only', '/supervisors-only')
    config.scan()

import os
import sys

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from wkcdd.models.base import (
    DBSession,
    Base,
)

from wkcdd.libs.import_project_data import (
    fetch_project_registration_data,
    fetch_report_form_data,
    fetch_meeting_form_reports,
    fetch_saic_meeting_form_reports
)
from wkcdd.libs.mis_location_integration import read_mis_csv


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def setup_database_engine(settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    return engine


def get_settings(argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    return get_appsettings(config_uri)


def get_engine(args):
    settings = get_settings(args)
    engine = setup_database_engine(settings)
    return engine


def main(argv=sys.argv):
    engine = get_engine(argv)
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)


def import_data(argv=sys.argv):
    engine = get_engine(argv)
    DBSession.configure(bind=engine)
    fetch_project_registration_data()
    fetch_report_form_data()
    fetch_meeting_form_reports()
    fetch_saic_meeting_form_reports()


def mis_encode_locations(argv=sys.argv):
    engine = get_engine(argv)
    DBSession.configure(bind=engine)
    read_mis_csv()

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'alembic',
    'psycopg2',
    'webtest',
    'pyramid_jinja2',
    'alembic',
    'fabric',
    # TODO: add pyramid_exc_logger
    'passlib',
    'Babel',
    'lingua',
    'requests',
    'flake8',
    'tablib',
    'deform'
]

setup(name='wkcdd',
      version='0.0',
      description='wkcdd',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='wkcdd',
      install_requires=requires,
      message_extractors={
          'wkcdd': [
              ('**.py', 'lingua_python', None),
              ('**.jinja2', 'jinja2', None)]
      },
      entry_points="""\
      [paste.app_factory]
      main = wkcdd:main
      [console_scripts]
      initialize_wkcdd_db = wkcdd.scripts.initializedb:main
      import_data = wkcdd.scripts.initializedb:import_data
      mis_encode_locations = wkcdd.scripts.initializedb:mis_encode_locations
      create_user = wkcdd.scripts.createuser:main
      """,
      )

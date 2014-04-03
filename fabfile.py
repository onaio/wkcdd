import os
from fabric.api import local, cd, run, settings, env, prefix

DEPLOYMENTS = {
    'prod': {
        'virtual_env': '/home/ubuntu/.virtualenvs/wkcdd_prod',
        'project_dir': '/home/ubuntu/wkcdd',
        'alembic_section': 'production'
    },
    'dev': {
        'virtual_env': '/home/vagrant/.virtualenvs/wkcdd_dev',
        'project_dir': '/home/vagrant/wkcdd'
    }
}


def deploy(deployment="prod", branch="master"):
    env.update(DEPLOYMENTS[deployment])
    virtual_env_command = 'source {}'.format(
        os.path.join(env.virtual_env, 'bin', 'activate'))
    with cd(env.project_dir):
        run("git checkout {branch}".format(branch=branch))
        run("git pull origin {branch}".format(branch=branch))
        run('find . -name "*.pyc" -exec rm -rf {} \;')

        with prefix(virtual_env_command):
            run("python setup.py test -q")
            run("python setup.py install")
            # run migrations
            run("alembic -n {0} upgrade head".format(
                env.get('alembic_section', 'alembic')))

    # Reload uWSGI
    run("/usr/local/bin/uwsgi --reload /var/run/wkcdd.pid")

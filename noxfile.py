import os

import nox

python_version = os.environ.get('PYTHON_VERSION', False)
if isinstance(python_version, str):
    python_version = python_version.split(':')

folders = ['common', 'fixtures', 'pre_run_scripts', 'suites']
files = ['noxfile.py', 'project.py', 'test_runner.py'] + folders
install_requires = ['pip', 'install', '-r', 'requirements-dev.txt', '--no-cache-dir']


@nox.session(python=python_version, name='isort')
def isort(session):
    """Run isort import sorter."""
    if python_version:
        session.run(*install_requires)
    command = ['isort']
    if session.posargs:
        command.append('-c')
    session.run(*(command + files))


@nox.session(python=python_version, name='yapf')
def yapf(session):
    """Run yapf code formatter."""
    if python_version:
        session.run(*install_requires)
    command = ['yapf', '-r', '-i']
    if session.posargs:
        command[-1] = '-d'

    session.run(*(command + files))


@nox.session(python=python_version, name='flake8')
def flake8(session):
    """Run flake8 linter."""
    if python_version:
        session.run(*install_requires)
    session.run('flake8', *files)

import json
import collections
import pprint

from packaging import version
import requests
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

WORKFLOW = {
    'name': 'Test Merseinne Twister',
    'on': {
        'push': {
            'branches': ['main'],
        },
        'pull_request': {
            'branches': ['main'],
        },
    },
    'jobs': {
        'do-the-twist': {
            'name': 'Do the Twist',
            'runs-on': "${{ matrix.os }}",  # Got to be something better
            'strategy': {
                'fail-fast': False,
                'matrix': {
                    'include': [],  # this is what we'll fill out
                },
            },
            'steps': [
                {
                    'uses': 'actions/checkout@v2'
                },
                {
                    'uses': 'actions/setup-python@v2',
                    'with': {
                        'python-version': '${{ matrix.python-version }}',
                        'architecture': '${{ matrix.python-architecture }}',
                    },
                },
                {
                    'run': 'python testme.py'
                },
            ]
        }
    }
}

# These are the known OSes on Github Actions
PLATFORMS = {
    'linux': ['ubuntu-20.04', 'ubuntu-18.04'],
    'win32': ['windows-2022', 'windows-2019', 'windows-2016'],
    'darwin': ['macos-11', 'macos-10.15']
}


def main():
    manifest = requests.get('https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json')
    n_includes = 0

    # {2.7: {2.7.17: [data dicts]}}, then sort inner keys and take last one
    python_major_versions = collections.defaultdict(
            lambda: collections.defaultdict(list))

    for data in json.loads(manifest.text):
        for release in data['files']:
            for target_os in PLATFORMS[release['platform']]:
                n_includes += 1
                include_dict = {
                    'os': target_os,
                    'python-version': data['version'],
                    'python-architecture': release['arch'],
                }

                major_version = '.'.join(data['version'].split('.')[:2])
                python_major_versions[major_version][
                    data['version']].append(include_dict)

    latest_minor_versions = {}
    for major_version, data in python_major_versions.items():
        # packaging.version function allows for proper python version
        # comparisons so we don't accidentally end up with an alpha when the
        # latest release is really a bugfix release.
        latest_minor_versions[major_version] = sorted(
            data, key=version.parse)[-1]

    pprint.pprint(latest_minor_versions)

    n_actually_included = 0
    for major_version, minor_version in latest_minor_versions.items():
        include_dicts = python_major_versions[major_version][minor_version]
        n_actually_included += len(include_dicts)
        WORKFLOW['jobs']['do-the-twist']['strategy']['matrix'][
            'include'].extend(include_dicts)

    print(f'Found {n_includes} python version combinations, '
          f'{n_actually_included} are the latest version per major release.')

    with open('.github/workflows/test-twister.yml', 'w') as workflow_file:
        workflow_file.write(dump(WORKFLOW, Dumper=Dumper))


if __name__ == '__main__':
    main()

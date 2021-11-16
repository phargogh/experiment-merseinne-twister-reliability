import json

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
                    'uses': 'actions/setup-python@v1',
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
    for data in json.loads(manifest.text):
        for release in data['files']:
            for target_os in PLATFORMS[release['platform']]:
                n_includes += 1
                include_dict = {
                    'os': target_os,
                    'python-version': data['version'],
                    'python-architecture': release['arch'],
                }
                WORKFLOW['jobs']['do-the-twist']['strategy']['matrix'][
                    'include'].append(include_dict)

    print(f'Found {n_includes} python version combinations')

    with open('.github/workflows/test-twister.yml', 'w') as workflow_file:
        workflow_file.write(dump(WORKFLOW, Dumper=Dumper))


if __name__ == '__main__':
    main()

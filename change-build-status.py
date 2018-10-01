#!/usr/bin/env python

```
This script is used to update the build status on a commit/PR in Bamboo.
```

import sys
import argparse
import yaml
import requests
import json
import os

BUILD_STATUS_RESOURCE = 'https://code.example.net/rest/build-status/1.0/commits/' #bitbucket URL
args = ''
commit = ''
build_url = ''
build_key = ''
status = ''
username = ''
password = ''

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('commit_hash',
                        help='Hash of the commit whose build you want to be changed',
                        type=str)
    parser.add_argument('build_url',
                        help='URL of the build whose status will be changed',
                        type=get_build_key)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--successful',
                       help='Change the build to SUCCESSFUL',
                       action='store_true')
    group.add_argument('--failed',
                       help='Change the build to FAILED',
                       action='store_true')
    args = parser.parse_args()
    return args

def get_creds():
    home = os.path.expanduser('~')
    credentials_file = home + '/.credentials'
    if os.path.isfile(credentials_file):
        credentials = yaml.load(open(credentials_file))
        username = credentials['ldap']['username']
        password = credentials['ldap']['password']
        return username, password
    else:
        print(credentials_file + ' does not exist.')
        sys.exit(1)

def get_build_key(url):
    if 'bamboo.example.net' in url: #bamboo URL
        key = url.split('/')[-1].rsplit('-', 1)[0]
        return url, key
    elif 'drone.example.net' in url: #drone URL
        key = 'Drone'
        return url, key
    else:
        msg = 'Not a valid build URL.'
        raise argparse.ArgumentTypeError(msg)

def main():
    args = get_args()
    commit = args.commit_hash
    build_url, build_key = args.build_url
    status = 'SUCCESSFUL' if args.successful else 'FAILED'
    username, password = get_creds()

    headers = { 'Content-Type': 'application/json' }
    data = json.dumps({ 'state': status,
                        'key': build_key,
                        'url': build_url })
    r = requests.post(BUILD_STATUS_RESOURCE+commit, headers=headers, auth=(username, password), data=data)

    if str(r.status_code) == "204":
        print('Updated build status.')
    else:
        print('Error while updating build status.')


if __name__ == '__main__':
    main()

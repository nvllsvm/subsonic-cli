#!/usr/bin/env python3
from pprint import pprint
import argparse
import configparser
import hashlib
import random
import sys

import requests


class SubsonicError(Exception):
    """Subsonic API error occured"""


class Subsonic:

    API_VERSION = '1.15.0'
    CLIENT_NAME = 'python-subsonic'
    RESPONSE_FORMAT = 'json'
    STREAMING_METHODS = [
        'download',
        'getCoverArt',
        'stream'
    ]

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def request(self, method, parameters):
        params = self.get_default_params(self.username, self.password)
        params.update(parameters)

        url = '{}/rest/{}.view'.format(self.url, method)

        if method in self.STREAMING_METHODS:
            return self._stream(url, params)
        else:
            return self._request(url, params)

    def _stream(self, url, parameters):
        response = requests.get(url, params=parameters, stream=True)
        if response.headers['Content-Type'].startswith('application/json'):
            print(response.json())
            raise NotImplementedError
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                sys.stdout.buffer.write(chunk)

    def _request(self, url, parameters):
        response = requests.get(url, params=parameters)
        response_body = response.json()
        if 'error' in response_body:
            pprint(response_body)
            raise SubsonicError(
                '{} - {}'.format(
                    response_body['error'],
                    response_body['message']
                )
            )
        response_body = response_body['subsonic-response']
        response_body.pop('version')
        if response_body.pop('status') != 'ok':
            pprint(response.json())
            raise NotImplementedError
        elif len(response_body) == 1:
            return response_body.popitem()[1]
        else:
            return response_body

    def get_default_params(self, username, password):
        salt, token = self.get_salt_and_token(password)
        return {
            'v': self.API_VERSION,
            'c': self.CLIENT_NAME,
            'f': self.RESPONSE_FORMAT,
            'u': username,
            's': salt,
            't': token
        }

    @staticmethod
    def get_salt_and_token(password):
        salt = random.randint(0, 100000)
        m = hashlib.md5('{}{}'.format(password, salt).encode())
        token = m.hexdigest()
        return salt, token


def read_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    config = config['subsonic']
    return {
        'username': config['username'],
        'password': config['password'],
        'url': config['url']
    }


def main():
    parser = argparse.ArgumentParser(
        description='Subsonic API command line interface'
    )
    parser.add_argument('-c', '--config', help='Config file')
    parser.add_argument('method', help='Subsonic method to invoke')
    parser.add_argument('-p', '--parameter', nargs=2, action='append',
                        default=[],
                        help='Parameter to include when making the requst')
    args = parser.parse_args()

    config = read_config(args.config)
    subsonic = Subsonic(**config)
    response = subsonic.request(
        args.method,
        {p[0]: p[1] for p in args.parameter}
    )
    pprint(response)


if __name__ == '__main__':
    main()

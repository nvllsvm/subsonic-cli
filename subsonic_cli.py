#!/usr/bin/env python3
import argparse
import configparser
import hashlib
import json
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
            dump_json(response_body)
            raise SubsonicError(
                '{} - {}'.format(
                    response_body['error'],
                    response_body['message']
                )
            )
        return response_body

    @staticmethod
    def format_response_body(body):
        body = body['subsonic-response']
        if body.pop('status') != 'ok':
            dump_json(body)
            raise NotImplementedError
        body.pop('version')
        if len(body) == 1:
            return body.popitem()[1]
        else:
            return body

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


def dump_json(data):
    json.dump(data, sys.stdout, sort_keys=True, indent=2)
    sys.stdout.write('\n')


def read_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    config = config['subsonic-cli']
    return {
        'username': config['username'],
        'password': config['password'],
        'url': config['url']
    }


def main():
    parser = argparse.ArgumentParser(
        description='Subsonic API command line interface'
    )
    parser.add_argument('-c', '--config', help='Config file', required=True)
    parser.add_argument('method', help='Subsonic method to invoke')
    parser.add_argument('-p', '--parameter', nargs=2, action='append',
                        default=[],
                        help='Parameter to include when making the requst')
    parser.add_argument('-f', '--full-response', action='store_const',
                        const=True)
    args = parser.parse_args()

    config = read_config(args.config)

    subsonic = Subsonic(**config)
    response = subsonic.request(
        args.method,
        {p[0]: p[1] for p in args.parameter}
    )
    if not args.full_response:
        response = subsonic.format_response_body(response)
    dump_json(response)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
import argparse
import configparser
import contextlib
import hashlib
import json
import random
import sys
import urllib.error
import urllib.parse
import urllib.request


class SubsonicError(Exception):
    """Subsonic API error occured"""


class Subsonic:

    API_VERSION = '1.15.0'
    CLIENT_NAME = 'python-subsonic'
    RESPONSE_FORMAT = 'json'
    STREAMING_ENDPOINTS = [
        'download',
        'getCoverArt',
        'stream'
    ]

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def request(self, endpoint, parameters):
        query = self.get_default_query(self.username, self.password)
        query.update(parameters)

        url = '{}/rest/{}.view'.format(self.url, endpoint)

        with self._request('GET', url, query=query) as response:
            if endpoint in self.STREAMING_ENDPOINTS:
                while True:
                    chunk = response.read(1024)
                    if chunk:
                        sys.stdout.buffer.write(chunk)
                    else:
                        break
            else:
                body = json.loads(response.read())
                if 'error' in body:
                    dump_json(body)
                    raise SubsonicError(
                        '{} - {}'.format(body['error'], body['message'])
                    )
                return body

    @contextlib.contextmanager
    def _request(self, method, url, query=None, timeout=60):
        if query is not None:
            query = urllib.parse.urlencode(query)
            url = urllib.parse.urlunsplit(
                urllib.parse.urlsplit(url)._replace(query=query)
            )

        r = urllib.request.Request(url, method=method)
        try:
            with urllib.request.urlopen(r, timeout=timeout) as response:
                yield response
        except urllib.error.HTTPError as error:
            yield error.fp

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

    def get_default_query(self, username, password):
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
    json.dump(data, sys.stdout, sort_keys=True, indent=2, ensure_ascii=False)
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
    parser.add_argument('endpoint', help='Subsonic endpoint to invoke')
    parser.add_argument('-p', '--parameter', nargs=2, action='append',
                        default=[],
                        help='Parameter to include when making the requst')
    parser.add_argument('-f', '--full-response', action='store_true')
    args = parser.parse_args()

    config = read_config(args.config)

    subsonic = Subsonic(**config)
    response = subsonic.request(
        args.endpoint,
        {p[0]: p[1] for p in args.parameter}
    )
    if not args.full_response and response:
        response = subsonic.format_response_body(response)
    dump_json(response)


if __name__ == '__main__':
    main()

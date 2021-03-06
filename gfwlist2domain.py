#!/usr/bin/python
# -*- coding: utf-8 -*-

import pkgutil
import urlparse
import json
import logging
from argparse import ArgumentParser

__all__ = ['main']


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-i', '--input', dest='input',
                      help='path to gfwlist', metavar='GFWLIST', default='gfwlist.txt')
    parser.add_argument('-o', '--output', dest='output',
                      help='path to output pac', metavar='PAC', default='pac.conf')
    return parser.parse_args()


def decode_gfwlist(content):
    # decode base64 if have to
    try:
        return content.decode('base64')
    except:
        return content


def get_hostname(something):
    try:
        # quite enough for GFW
        if not something.startswith('http:'):
            something = 'http://' + something
        r = urlparse.urlparse(something)
        return r.hostname
    except Exception as e:
        logging.error(e) 
        return None


def add_domain_to_set(s, something):
    hostname = get_hostname(something)
    if hostname is not None:
        if hostname.startswith('.'):
            hostname = hostname.lstrip('.')
        if hostname.endswith('/'):
            hostname = hostname.rstrip('/')
        if hostname:
            s.add(hostname)


def parse_gfwlist(content):
    builtin_rules = pkgutil.get_data(__name__,'builtin.txt').splitlines(False)
    gfwlist = content.splitlines(False)
    domains = set(builtin_rules)
    for line in gfwlist:
        if line.find('.*') >= 0:
            continue
        elif line.find('*') >= 0:
            line = line.replace('*', '/')
        if line.startswith('!'):
            continue
        elif line.startswith('['):
            continue
        elif line.startswith('@'):
            # ignore white list
            continue
        elif line.startswith('||'):
            add_domain_to_set(domains, line.lstrip('||'))
        elif line.startswith('|'):
            add_domain_to_set(domains, line.lstrip('|'))
        elif line.startswith('.'):
            add_domain_to_set(domains, line.lstrip('.'))
        else:
            add_domain_to_set(domains, line)
    # TODO: reduce ['www.google.com', 'google.com'] to ['google.com']
    return '\n'.join(domains)


def main():
    args = parse_args()
    with open(args.input, 'rb') as f:
        content = f.read()
    content = decode_gfwlist(content)
    domains = parse_gfwlist(content)
    with open(args.output, 'wb') as f:
        f.write(domains)
        

if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""A command line tools for CMDB variants browser

Author: Shujia Huang
Date: 2018-11-22

"""

import argparse
import os
import sys
import gzip

import json
import yaml

from urllib import urlencode
from urllib2 import Request, urlopen, HTTPError

if sys.version_info.major != 2:
    raise Exception('This tool supports only python2')

argparser = argparse.ArgumentParser(description='Manage authentication for CMDB API and do querying from command line.')
commands = argparser.add_subparsers(dest='command', title='Commands')

login_command = commands.add_parser('login', help='Authorize access to CMDB API.')
logout_command = commands.add_parser('logout', help='Logout CMDB.')
token_command = commands.add_parser('print-access-token', help='Display access token for CMDB API.')

login_command.add_argument('-k', '--token', type=str, required=True, dest='token',
                           help='CMDB API access key(Token).')

annotate_command = commands.add_parser('annotate', help='Annotate input VCF.',
                                       description='Input VCF file. Multi-allelic variant records in input VCF must be split into multiple bi-allelic variant records.')
annotate_command.add_argument('-i', '--vcffile', metavar='name', type=str, required=True, dest='in_vcffile',
                              help='input VCF file.')
annotate_command.add_argument('-f', '--filter', metavar='expression', required=False, type=str, dest='filter',
                              help='Filtering expression.')

query_variant_command = commands.add_parser('query-variant',
                                            help='Query variant by variant identifier or by chromosome name and chromosomal position.',
                                            description='Query variant by identifier chromosome name and chromosomal position.')
query_variant_command.add_argument('-c', '--chromosome', metavar='name', type=str, dest='chromosome', help='Chromosome name.')
query_variant_command.add_argument('-p', '--position', metavar='base-pair', type=int, dest='position', help='Position.')
# query_variant_command.add_argument('-v', '--variant', metavar='chrom-pos-ref-alt/rs#', type=str, dest='variant_id',
#                                    help='Variant identifier CHROM-POS-REF-ALT or rs#.')
# query_variant_command.add_argument('-o', '--output', required=False, choices=['json', 'vcf'], default='json',
#                                    dest='format', help='Output format.')

USER_HOME = os.path.expanduser("~")
CMDB_DIR = '.cmdb'
CMDB_TOKENSTORE = 'authaccess.yaml'

CMDB_DATASET_VERSION = 'CMDB_hg19_v1.0'
CMDB_API_VERSION = 'v1.0'
CMDB_API_MAIN_URL = 'https://db.cngb.org/cmdb/api/{}'.format(CMDB_API_VERSION)

CMDB_VCF_HEADER = [
    '##fileformat=VCFv4.2',
    '##FILTER=<ID=LowQual,Description="Low quality">',
    '##INFO=<ID=CMDB_AN,Number=1,Type=Integer,Description="Number of Alleles in Samples with Coverage from {}">'.format(
        CMDB_DATASET_VERSION),
    '##INFO=<ID=CMDB_AC,Number=A,Type=Integer,Description="Alternate Allele Counts in Samples with Coverage from {}">'.format(
        CMDB_DATASET_VERSION),
    '##INFO=<ID=CMDB_AF,Number=A,Type=Float,Description="Alternate Allele Frequencies from {}">'.format(CMDB_DATASET_VERSION),
    '##INFO=<ID=CMDB_FILTER,Number=A,Type=Float,Description="Filter from {}">'.format(CMDB_DATASET_VERSION),
    '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO'
]


class CMDBException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def load_version():
    if not authaccess_exists():
        print "No access tokens found. Please login first.\n"
        return

    tokenstore = read_tokenstore()
    return tokenstore["version"]


class requests(object):
    # this implements the parts we need of the real `requests` module
    @staticmethod
    def get(url, headers={}, params=None):
        if params:
            url += '?' + urlencode(params)

        r = Request(url=url, headers=headers)
        try:
            response = urlopen(r)
        except HTTPError:
            response = None

        return _requests_response(response)

    @staticmethod
    def post(url, headers={}, data=None):
        if data is not None and isinstance(data, dict):
            data = urlencode(data)

        r = Request(url, headers=headers, data=data)
        return _requests_response(urlopen(r))


class _requests_response(object):
    def __init__(self, response):

        if response:
            self.status_code = response.getcode()
            self._json = json.load(response.fp)
        else:
            self.status_code = 404
            self._json = None

    def json(self):
        return self._json


class _requests_exceptions(object):
    pass


requests.exceptions = _requests_exceptions
requests.exceptions.RequestException = HTTPError


def authaccess_exists():
    return os.path.isfile(os.path.join(USER_HOME, CMDB_DIR, CMDB_TOKENSTORE))


def create_tokenstore():
    p = os.path.join(USER_HOME, CMDB_DIR)
    if not os.path.isdir(p):
        os.mkdir(p, 0700)

    p = os.path.join(p, CMDB_TOKENSTORE)
    if not os.path.isfile(p):
        # create file
        open(p, 'a').close()
        os.chmod(p, 0600)


def read_tokenstore():
    token_path = os.path.join(USER_HOME, CMDB_DIR, CMDB_TOKENSTORE)
    with open(token_path, 'r') as I:
        tokenstore = yaml.load(I)

        access_token = tokenstore.get('access_token', None)
        if access_token is None or not isinstance(access_token, basestring):
            raise CMDBException('Invalid or outdated access token. You may need to run login.')

        return tokenstore


def write_tokenstore(token):
    file_path = os.path.join(USER_HOME, CMDB_DIR, CMDB_TOKENSTORE)
    with open(file_path, 'w') as tokenstore:
        token_obj = {
            "access_token": token,
            "version": CMDB_DATASET_VERSION
        }
        yaml.dump(token_obj, tokenstore)

    os.chmod(file_path, 0600)


def login(token):
    # Test the token is available or not
    test_url = "https://db.cngb.org/cmdb/api/v1.0/variant?token={}&type=position&query=chr17-41234470".format(token)
    cmdb_response = requests.get(test_url)

    if cmdb_response.status_code != 201:
        raise CMDBException('Error while obtaining your token with CMDB API authentication server.'
                            'You may do not have the API access or the token is wrong.\n')

    if not authaccess_exists():
        create_tokenstore()

    write_tokenstore(token)
    sys.stdout.write("Done.\nYou are signed in now.\n")

    return


def logout():
    # logout by delete the tokenstore file
    if not authaccess_exists():
        sys.stderr.write("Don't find any your access token, no need to logout.\n")
        return

    file_path = os.path.join(USER_HOME, CMDB_DIR, CMDB_TOKENSTORE)
    os.remove(file_path)
    sys.stdout.write("Done.\nLogout successful.\n")

    return


def print_access_token():

    if not authaccess_exists():
        sys.stderr.write('No access tokens found. Print nothing.\n')
        return

    tokenstore = read_tokenstore()
    print (tokenstore['access_token'])


def _query_paged(headers, url):
    page_no = 1
    while url:
        cmdb_response = requests.get(url, headers=headers)
        if cmdb_response.status_code != 200:
            if cmdb_response.status_code == 400:
                raise CMDBException(cmdb_response.json().get('error', 'Failed to query data.'))
            else:
                cmdb_response.raise_for_status()

        cmdb_response_data = cmdb_response.json()
        if cmdb_response_data['format'] == 'vcf' and page_no == 1:
            for line in cmdb_response_data['meta']:
                yield line

            yield cmdb_response_data['header']

        for item in cmdb_response_data['data']:
            yield item

        url = cmdb_response_data['next']
        page_no += 1


def _query_nonpaged(token, url):
    cmdb_response = requests.get("{}&token={}".format(url, token))
    if cmdb_response.status_code != 201:
        if cmdb_response.status_code == 403:
            raise CMDBException(cmdb_response.json().get('error', 'Failed to query data.'))

        elif cmdb_response.status_code == 404:
            pass
        else:
            cmdb_response.raise_for_status()

    return cmdb_response.json()


def query_variant(chromosome, position):
    if not authaccess_exists():
        sys.stderr.write('No access tokens found. Please login first.\n')
        return

    tokenstore = read_tokenstore()
    if chromosome is None or position is None:
        raise CMDBException('Provide both "-c,--chromosome" and "-p,--position".')

    query_url = '{}/variant?&type=position&query={}-{}'.format(CMDB_API_MAIN_URL, chromosome, position)
    return _query_nonpaged(tokenstore["access_token"], query_url)


def annotate(infile, filter=None):
    if not authaccess_exists():
        raise CMDBException('[ERROR] No access tokens found. Please login first.\n')

    data_version = load_version()
    with gzip.open(infile) if infile.endswith('.gz') else open(infile) as I:

        for in_line in I:

            if in_line.startswith('#'):
                if in_line.startswith('##'):
                    sys.stdout.write('{}\n'.format(in_line.rstrip()))

                elif in_line.startswith('#CHROM'):

                    sys.stdout.write(
                        '##INFO=<ID=CMDB_AN,Number=1,Type=Integer,Description="Number of Alleles in Samples with Coverage from {}">\n'.format(
                            data_version))
                    sys.stdout.write(
                        '##INFO=<ID=CMDB_AC,Number=A,Type=Integer,Description="Alternate Allele Counts in Samples with Coverage from {}">\n'.format(
                            data_version))
                    sys.stdout.write(
                        '##INFO=<ID=CMDB_AF,Number=A,Type=Float,Description="Alternate Allele Frequencies from {}">\n'.format(
                            data_version))
                    sys.stdout.write(
                        '##INFO=<ID=CMDB_FILTER,Number=A,Type=Float,Description="Filter from {}">\n'.format(
                            data_version))
                    sys.stdout.write('{}\n'.format(in_line.rstrip()))

                continue

            in_fields = in_line.rstrip().split()
            if 'chr' not in in_fields[0].lower():
                in_fields[0] = 'chr' + in_fields[0].lower()

            chromosome = in_fields[0]
            position = int(in_fields[1])
            ref = in_fields[3]
            alt = in_fields[4]  # assume bi-allelic

            cmdb_variant = query_variant(chromosome, position)
            # Must just be one element in the `list`
            if cmdb_variant:
                cmdb_variant = cmdb_variant[0]

            # ignore `chr` in `variant` which could be compared with variant-id in CMDB
            variants = ['-'.join([chromosome.split('chr')[-1], str(position), ref, a]).upper()
                        for a in alt.split(',')]

            if cmdb_variant is None or (cmdb_variant and (cmdb_variant['variant_id'] not in variants)):
                sys.stdout.write('{}\n'.format('\t'.join(in_fields)))

            else:
                new_info = {
                    'CMDB_AN': 'CMDB_AN={}'.format(cmdb_variant['allele_num']),
                    'CMDB_AC': 'CMDB_AC={}'.format(cmdb_variant['allele_count']),
                    'CMDB_AF': 'CMDB_AF={}'.format(cmdb_variant['allele_freq']),
                    'CMDB_FILTER': 'CMDB_FILTER={}'.format(cmdb_variant['filter_status'])
                }

                info = in_fields[7]
                if info != '.':
                    for c in info.split(';'):
                        k = c.split('=')[0]
                        if k not in new_info:
                            new_info[k] = c

                info = ';'.join([new_info[k] for k in sorted(new_info.keys())])
                if len(in_fields) > 8:

                    sys.stdout.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                        chromosome, position, in_fields[2], ref, alt, in_fields[5], in_fields[6], info,
                        '\t'.join(in_fields[8:]))
                    )
                else:
                    sys.stdout.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                        chromosome, position, in_fields[2], ref, alt, in_fields[5], in_fields[6], info)
                    )
    return


def run_query_variant(chromosome, position):

    if not authaccess_exists():
        raise CMDBException('[ERROR] No access tokens found. Please login first.\n')

    sys.stdout.write('%s\n' % '\n'.join(CMDB_VCF_HEADER))
    for cmdb_variant in query_variant(chromosome, position):
        vcf_line = [
            'chr' + cmdb_variant['chrom'],
            cmdb_variant['pos'],
            cmdb_variant['rsid'],
            cmdb_variant['ref'],
            cmdb_variant['alt'],
            cmdb_variant['site_quality'],
            cmdb_variant['filter_status'],
            'CMDB_AF={},CMDB_AC={},CMDB_AN={}'.format(
                cmdb_variant['allele_freq'],
                cmdb_variant['allele_count'],
                cmdb_variant['allele_num']
            )
        ]
        sys.stdout.write('%s\n' % '\t'.join(map(str, vcf_line)))


def main():
    # entry function
    args = argparser.parse_args()
    try:
        if args.command == 'login':
            login(args.token)

        elif args.command == 'logout':
            logout()

        elif args.command == 'print-access-token':
            print_access_token()

        elif args.command == 'query-variant':
            if 'chr' not in args.chromosome.lower():
                args.chromosome = 'chr' + args.chromosome.lower()

            run_query_variant(args.chromosome.lower(), args.position)

        elif args.command == 'annotate':
            annotate(args.in_vcffile, args.filter)

    except CMDBException as e:
        print (e)


if __name__ == '__main__':
    main()


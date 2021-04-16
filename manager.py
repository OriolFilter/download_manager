#!/usr/bin/env python3

"""
@author OriolFilter
@date 16/4/2021
"""

from classes import Manager, Config
import argparse as argparse

version = '0.1.2'
# Args
parser = argparse.ArgumentParser(description='Python middleman for youtube-dl')
parser.add_argument('-a', '--audio_only', action='store_true', help='Only download files as audio files (as .mp3)')
parser.add_argument('-o', '--output', help='Desired path/name to store the file as, if not specified will use the '
                                           'working directory')
parser.add_argument('-l', '--link', action='append', help='Links to download')
parser.add_argument('-f', '--file', action='append', help='Instead of a link, use a file that contains links, '
                                                          'distributing them in each line')
parser.add_argument('-v', '--version', action='store_true', help='Prints the version')
parser.add_argument('-q', '--quiet', action='store_true', help='Limits the output to minimal responses')
parser.add_argument('-da', '--download_archive', action='store', help='Download only links not listed in the file, '
                                                                      'and appending to the file the links downloaded')
parser.add_argument('-thi', '--threading_instances', action='store', help='Number of threading instances to ')

args = parser.parse_args()

""" Main """
if args.version:
    print(f'Download manager version: {version}')
else:
    conf = Config(dl_link=args.link, dl_file=args.file, output=args.output, audio_only=args.audio_only,
                  archive=args.download_archive, threading_instances=args.threading_instances, quiet=args.quiet)
    manager = Manager(config=conf)
    manager.start_downloads()

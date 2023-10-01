import os
import sys
from os import path

ROOT = path.realpath(path.dirname(__file__))
sys.path.insert(0, path.join(ROOT, "python"))

import json
import logging
from argparse import ArgumentParser

from crawler import index, api, log

common_parser = ArgumentParser("common", add_help=False)
gparser = common_parser.add_argument_group("common options")
gparser.add_argument(
        "-v", "--verbosity",
        metavar="LEVEL",
        default=log.level2name(log.INFO),
        choices=log.LOG_NAMES,
        help="print log level, available options: {}".format(
            ",".join(log.LOG_NAMES)))

parser = ArgumentParser(
        "mouse_web",
        parents=[ common_parser, ])
sub_parser = parser.add_subparsers(
        metavar="commands",
        help = "Multi-tools for Crawler")


index_parser = sub_parser.add_parser(
        "index",
        parents=[ common_parser, ],
        help = "teacher link indexer")

ALL_FUNCS = {}
def register_arg(func):
    ALL_FUNCS[func.__name__] = func
    index_parser.add_argument(
            "--{}".format(func.__name__),
            action="store_true",
            help=func.__doc__)

register_arg(api.hit_edu_cn)

def main(args):
    log.Init(log.name2level(args.verbosity))
    for name, func in ALL_FUNCS.items():
        if getattr(args, name, False):
            func()

    logging.info("index done.")


index_parser.set_defaults(func=main)

if __name__ == "__main__":
    args = parser.parse_args(sys.argv[1:])
    args.func(args)


#!/usr/bin/env python3

import os
import sys
from os import path

ROOT = path.realpath(path.dirname(__file__))
sys.path.insert(0, path.join(ROOT, "python"))

import json
import logging
from argparse import ArgumentParser

from crawler import index, api, log, data, utils

common_parser = ArgumentParser("common", add_help=False)
common_parser.add_argument(
        "-v", "--verbosity",
        metavar="L",
        default=log.level2name(log.INFO),
        choices=log.LOG_NAMES,
        help="print log level: {}".format(
            ",".join(log.LOG_NAMES)))

parser = ArgumentParser(
        "mouse_web",
        parents=[ common_parser, ])
sub_parser = parser.add_subparsers(title="COMMANDS")
index_parser = sub_parser.add_parser(
        "index",
        parents=[ common_parser, ],
        help = "teacher link indexer")

data_parser = sub_parser.add_parser(
        "data",
        parents=[ common_parser, ],
        help = "teacher data generator")


INDEX_FUNCS = {}
def register_index_arg(func):
    INDEX_FUNCS[func.__name__] = func
    index_parser.add_argument(
            "--{}".format(func.__name__),
            action="store_true",
            help=func.__doc__)

DATA_FUNCS = {}
def register_data_arg(func):
    DATA_FUNCS[func.__name__] = func
    data_parser.add_argument(
            "--{}".format(func.__name__),
            action="store_true",
            help=func.__doc__)

for func in dir(api):
    if func.startswith("_") or "edu_cn" not in func:
        continue
    register_index_arg(getattr(api, func))

register_data_arg(data.hit_edu_cn)
register_data_arg(data.sicau_edu_cn)
register_data_arg(data.bjut_edu_cn)

data_parser.add_argument(
    "-o", "--output",
    default=path.join(utils.ROOT, "sources/data"),
    help='data save path')

def index_main(args):
    log.Init(log.name2level(args.verbosity))
    for name, func in INDEX_FUNCS.items():
        if getattr(args, name, False):
            func()

    logging.info("index done.")

def data_main(args):
    log.Init(log.name2level(args.verbosity))
    for name, func in DATA_FUNCS.items():
        if getattr(args, name, False):
            func(args.output)


index_parser.set_defaults(func=index_main)
data_parser.set_defaults(func=data_main)

if __name__ == "__main__":
    args = parser.parse_args(sys.argv[1:])
    args.func(args)


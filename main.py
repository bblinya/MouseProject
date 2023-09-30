import os
import sys
from os import path

ROOT = path.realpath(path.dirname(__file__))
sys.path.insert(0, path.join(ROOT, "python"))

import json
from argparse import ArgumentParser

from crawler import index

parser = ArgumentParser("mouse_web")
sub_parser = parser.add_subparsers(
        metavar="commands",
        help = "Multi-tools for Crawler")

index_parser = sub_parser.add_parser(
        "index", help = "teacher link indexer")
index_parser.add_argument("conf", help="config file")
index_parser.set_defaults(func=index.main)

if __name__ == "__main__":
    args = parser.parse_args(sys.argv[1:])
    args.func(args)


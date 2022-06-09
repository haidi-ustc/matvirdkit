#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2021.

import argparse
import sys
import itertools
from matvirdkit.builder.base import main as builder_main
from matvirdkit.creator.base import main as creator_main
from matvirdkit import NAME, SHORT_CMD

__author__ = ""
__copyright__ = ""
__maintainer__ = "Haidi Wang"
__email__ = "haidi@hfut.edu.cn"

def get_version():
  try:
     from matvirdkit._version import version
  except:
     version="Unknow" 
  return version 

def main():
    parser = argparse.ArgumentParser(prog=SHORT_CMD,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=f"""Desctiption:\n------------
{SHORT_CMD} is collection of toolkits for preparing and quering the data of matvird database.
To see the options for the sub-commands, type "{SHORT_CMD} sub-command -h".""")
    parser.add_argument('-v', '--version', action='version', version=get_version(),help='Display version')

    subparsers = parser.add_subparsers()

    #-------------
    # builder
    parser_build = subparsers.add_parser(
        "build", help="Generating data set for matvird.")
    parser_build.add_argument('-c','--config', type=str, default='info.json', help="The information file. Supported format: ['info.json','info.yaml']")
    parser_build.set_defaults(func=builder_main)
    
    #-------------
    #creator
    parser_create= subparsers.add_parser(
        "create", help="Write the data into database")
    parser_create.add_argument('-c','--config', type=str, default='db.json', help="The DB setting file. ")
    parser_create.set_defaults(func=creator_main)
    
    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        # argcomplete not present.
        pass

    args = parser.parse_args()

    try:
        getattr(args, "func")
    except AttributeError:
        parser.print_help()
        sys.exit(0)
    args.func(args)

if __name__ == "__main__":
    main() 

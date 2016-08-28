#!/usr/bin/env python
import argparse

from androtoolbox.log import is_valid_log_level, set_loggable_level_for_tags


def main():
    description = "Set the loggable level for a list of tags"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-l', '--level', default='VERBOSE', help='Log level for all tags')
    parser.add_argument('tags', metavar='tag', nargs='+', help="Log tag to set")
    options = parser.parse_args()
    if not is_valid_log_level(options.level):
        parser.error("%s is an invalid log level" % options.level)
    set_loggable_level_for_tags(options.tags, options.level)

if __name__ == "__main__":
    main()

#!/usr/bin/env python
import argparse

from androtoolbox.shared_pref import SharedPref


def update_shared_pref(package, pref_name, updates):
    shared_pref = SharedPref.from_device(package, pref_name)
    shared_pref.update(updates)
    shared_pref.to_device(package, pref_name)


def main():
    description = "Update shared preferences of a packages"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('package', help="The package name")
    parser.add_argument('pref_name', help="The shared preference filename")
    parser.add_argument('-v', '--value', action='append', nargs=2, metavar=('key', 'value'))
    options = parser.parse_args()
    updates = dict(options.value)
    update_shared_pref(options.package, options.pref_name, updates)


if __name__ == '__main__':
    main()

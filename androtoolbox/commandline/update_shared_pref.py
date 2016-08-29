#!/usr/bin/env python
import argparse
import os
import tempfile
from androtoolbox.adb import adb
from androtoolbox.shared_pref import SharedPref, build_shared_pref_path


def read_shared_pref(package, pref_name):
    pref_device_path = build_shared_pref_path(package, pref_name)
    data = adb.shell("cat %s" % pref_device_path, use_su=True)
    return SharedPref.from_xml(data)


def write_shared_pref(package, pref_name, shared_pref):
    tmp_shared_file = tempfile.NamedTemporaryFile()
    shared_pref.to_file(tmp_shared_file)
    pref_device_path = build_shared_pref_path(package, pref_name)
    local_path = tmp_shared_file.name
    remote_tmp_path = "/data/local/tmp/%s" % os.path.basename(local_path)
    adb.push(tmp_shared_file.name, remote_tmp_path)
    adb.shell('mv %s %s' % (remote_tmp_path, pref_device_path), use_su=True)

    # We need to fix any permissions mix up
    adb.shell('chmod 0777 %s' % pref_device_path, use_su=True)


def update_shared_pref(package, pref_name, updates):
    shared_pref = read_shared_pref(package, pref_name)
    shared_pref.update(updates)
    write_shared_pref(package, pref_name, shared_pref)


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

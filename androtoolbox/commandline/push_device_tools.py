#!/usr/bin/env python
import argparse
import glob
import os

from androtoolbox.adb import adb
from androtoolbox import ROOT_DIR

DEFAULT_TARGET_PATH = '/data/local/tmp/bin'


def push_device_tools(target_path=DEFAULT_TARGET_PATH):
    adb.shell('mkdir -p %s' % target_path)
    tools_paths = glob.glob(os.path.join(ROOT_DIR, 'device_tools', 'arm', '*'))
    for local_path in tools_paths:
        remote_path = os.path.join(target_path, os.path.basename(local_path))
        adb.push(local_path, remote_path)

    adb.shell('chmod 0777 %s' % os.path.join(target_path, '*'))


def main():
    description = "Push device tools used by this framework to the device"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-t', '--target-path', default=DEFAULT_TARGET_PATH, help='The target path for tools')
    options = parser.parse_args()
    push_device_tools(options.target_path)


if __name__ == "__main__":
    main()

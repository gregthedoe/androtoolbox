#!/usr/bin/env python
import argparse
import os
import time

from androtoolbox.packages import pull_data

DEFAULT_DEVICE_TMP_STORAGE = '/data/local/tmp'


def pull_package_data(package, output_path, create_unique_dir=False, device_temp_storage=DEFAULT_DEVICE_TMP_STORAGE):
    if create_unique_dir:
        output_path = os.path.join(output_path, time.strftime("%Y%m%d%H%M"))
    else:
        output_path = output_path
    os.makedirs(output_path)
    pull_data(package, device_temp_storage, output_path)


def main():
    description = "Pull packages data from a device"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("package_name", help="Package's name we want to pull")
    parser.add_argument('-o', '--output-path', default='.', help="Output path to store packages data in")
    parser.add_argument('-c', '--create-unique-dir', default=False, action="store_true",
                        help="Create a unique dir inside the outpath path")
    parser.add_argument('-t', "--device-temp-storage", default=DEFAULT_DEVICE_TMP_STORAGE,
                        help="Device's temp storage used for copying")
    options = parser.parse_args()
    pull_package_data(options.package_name, options.output_path, options.create_unique_dir, options.device_temp_storage)


if __name__ == "__main__":
    main()

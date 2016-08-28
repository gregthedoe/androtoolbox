#!/usr/bin/env python
import argparse
import os
import time

from androtoolbox.packages import pull_data

DEFAULT_DEVICE_TMP_STORAGE = '/data/local/tmp'


def main():
    description = "Pull packages data from a device"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("package_name", help="Package's name we want to pull")
    parser.add_argument('-t', "--device-temp-storage", default=DEFAULT_DEVICE_TMP_STORAGE,
                        help="Device's temp storage used for copying")
    parser.add_argument('-o', '--output-path', default='.', help="Output path to store packages data in")
    parser.add_argument('-c', '--create-unique-dir', default=False, action="store_true",
                        help="Create a unique dir inside the outpath path")
    options = parser.parse_args()
    if options.create_unique_dir:
        output_path = os.path.join(options.output_path, time.strftime("%Y%m%d%H%M"))
    else:
        output_path = options.output_path
    os.makedirs(output_path)
    pull_data(options.package_name, options.device_temp_storage, output_path)


if __name__ == "__main__":
    main()

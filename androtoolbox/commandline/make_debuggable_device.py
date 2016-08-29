#!/usr/bin/env python
import argparse
from androtoolbox.adb import adb
from androtoolbox.process import kill

SETPROPEX_PATH = '/data/local/tmp/bin/setpropex'


def make_debuggable(kill_system_server=False, setpropex_path=SETPROPEX_PATH):
    adb.shell("%s ro.debuggable 1" % setpropex_path, use_su=True)
    adb.shell("%s ro.secure 0" % setpropex_path, use_su=True)
    if kill_system_server:
        kill('system_server')


def main():
    description = "Make the device debuggable"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--setpropex-path', default=SETPROPEX_PATH, help="The path for setpropex binary")
    parser.add_argument('-k', '--do-not-kill-system-server', default=False, action="store_true")
    options = parser.parse_args()
    kill_system_server = not options.do_not_kill_system_server
    make_debuggable(kill_system_server=kill_system_server, setpropex_path=options.setpropex_path)

if __name__ == "__main__":
    main()

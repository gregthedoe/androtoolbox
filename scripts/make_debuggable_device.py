import argparse
from androtoolbox.adb import adb
from androtoolbox.process import kill

SETPROPEX_PATH = '/data/local/tmp/bin/setpropex'


def make_debuggable(setpropex_path):
    adb.shell("%s ro.debuggable 1" % setpropex_path, use_su=True)
    adb.shell("%s ro.secure 0" % setpropex_path, use_su=True)


def main():
    description = "Make the device debuggable"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--setpropex-path', default=SETPROPEX_PATH, help="The path for setpropex binary")
    parser.add_argument('-k', '--do-not-kill-system-server', default=False, action="store_true")
    options = parser.parse_args()
    make_debuggable(options.setpropex_path)
    if not options.do_not_kill_system_server:
        kill('system_server')

if __name__ == "__main__":
    main()

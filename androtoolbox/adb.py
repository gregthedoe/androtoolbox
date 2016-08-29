from subprocess import check_output

_ADB_CMD = "adb"


class Commands:
    SHELL = "shell"
    PUSH = "push"
    PULL = "pull"
    INSTALL = "install"
    UNINSTALL = "uninstall"
    WAIT_FOR_DEVICE = "wait-for-device"


class Adb(object):
    def __init__(self, adb_cmd=_ADB_CMD, debug=False):
        self._debug = debug
        self._adb_cmd = adb_cmd

    def _exec(self, args, **kwargs):
        if self._debug:
            print args
        return check_output(args, **kwargs)

    def shell(self, command, use_su=False):
        args = [self._adb_cmd, Commands.SHELL]
        if use_su:
            args.append("su")
            args.append("-c")
        args.append(command)
        return self._exec(args)

    def push(self, local, remote):
        args = [self._adb_cmd, Commands.PUSH, local, remote]
        return self._exec(args)

    def pull(self, remote, local='.'):
        args = [self._adb_cmd, Commands.PULL, remote, local]
        return self._exec(args)

    def install(self, apk, forward_lock=False, reinstall_and_keep_data=False, install_on_sd_card=False):
        args = [self._adb_cmd, Commands.INSTALL]
        if forward_lock:
            args.append('-l')
        if reinstall_and_keep_data:
            args.append('-r')
        if install_on_sd_card:
            args.append('-s')
        args.append(apk)
        return self._exec(args)

    def uninstall(self, package, keep_data=False):
        args = [self._adb_cmd, Commands.UNINSTALL]
        if keep_data:
            args.append('-k')
        args.append(package)
        return self._exec(args)

    def wait_for_device(self):
        args = [self._adb_cmd, Commands.WAIT_FOR_DEVICE]
        return self._exec(args)

    def get_property(self, name=None):
        if not name:
            props = self.shell('getprop').splitlines()
            return dict((name.strip('[]'), value.strip('[]')) for name, value in
                        (prop.strip().split(': ') for prop in props))

        return self.shell('getprop %s' % name).strip()

    def set_property(self, name, value, use_su=False):
        self.shell('setprop %s %s' % (name, value), use_su)

    def file_exists(self, filepath, use_su=False):
        return self.shell('ls %s' % filepath, use_su=use_su).strip() == filepath

adb = Adb()

import attr
import re

from .adb import adb


@attr.s
class Process(object):
    name = attr.ib()
    user = attr.ib()
    pid = attr.ib(convert=int)
    parent_pid = attr.ib(convert=int)
    vsize = attr.ib(convert=int)
    rss = attr.ib(convert=int)
    wchan = attr.ib()
    pc = attr.ib()
    state = attr.ib()

    @classmethod
    def parse_from_line(cls, line):
        user, pid, ppid, vsize, rss, wchan, pc, state, name = line.split()
        return cls(name, user, pid, ppid, vsize, rss, wchan, pc, state)


def get_running_processes(filter=None):
    """
    Get all running processes, (optionally) matching a filter.

    :param filter: An optional regex to filter process names
    :type filter: str | None
    :rtype: list(Process)
    """
    raw_data = adb.shell('ps').splitlines()[1:]  # The first line is the table headers
    processes = [Process.parse_from_line(raw_data_line) for raw_data_line in raw_data]
    if filter:
        processes = [p for p in processes if re.search(filter, p.name)]
    return processes


def pid_of(process):
    """
    Get the PID of a running process

    :param process: The process name
    """
    processes = get_running_processes(process)
    if len(processes) != 1:
        return None
    return processes[0]


def kill(process):
    """
    Kill a running process. If the process

    note: Uses su
    :param process: The process' name or pid
    """
    try:
        pid = int(process)
    except ValueError:
        pid = pid_of(process)

    if pid:
        adb.shell('kill -9 %s', use_su=True)

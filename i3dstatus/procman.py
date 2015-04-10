"""
Responsible for starting processes.
"""
import os.path
import pkg_resources
import subprocess
import sys


def find_generator(name):
    """
    Find a generator and return the file name.

    1. If it's an absolute path (with ~ expansions), return resolved name
    2. If it's one of the bundled generators, resolve it
    3. Otherwise, assume it's on the PATH and return as-is
    """
    # Is this an absolute name?
    fullname = os.path.expanduser(name)
    if os.path.isabs(fullname) and os.path.exists(fullname):
        return fullname

    # Is it one of the included generators?
    pkgname = pkg_resources.resource_filename(__name__, 'generators/{}'.format(name))
    if os.path.exists(pkgname):
        return pkgname

    # Assume it's on the PATH
    return name


def start_generator(name):
    """
    Start a generator, given its partial name.

    * Closes stdin
    * Redirects stdout to stderr (so that it doesn't conflict with i3bar)

    Returns a Popen object of the started process.
    """
    exename = find_generator(name)
    proc = subprocess.Popen(
        [exename],
        stdin=subprocess.PIPE, stdout=sys.stderr)
    proc.stdin.close()
    return proc


def run_from_config(config, extras=()):
    """
    Entry point from startup.

    Loads a list of generators to start from general.generators
    """
    if 'general' in config and 'generators' in config['general']:
        for gen in config['general']['generators']:
            if gen not in extras:
                start_generator(gen)
    for gen in extras:
        start_generator(gen)

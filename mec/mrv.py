#!/usr/bin/env python

import os
import tomllib
import fire
import libtmux

from .reg import CONFIG_DIR

# get specification
with (CONFIG_DIR / 'mrv.toml').open('rb') as fid:
    specs = tomllib.load(fid)

# tmux server
server = libtmux.Server()

# operations
def get_session(unit):
    if server.has_session(unit):
        return server.sessions.get(session_name=unit)
    return None

def is_running(unit):
    return server.has_session(unit)

def dispatch(func, unit, *args):
    if unit is None:
        for u in specs:
            func(u)
    else:
        if unit in specs:
            func(unit, *args)
        else:
            print(f'{unit}: not found')

def do_info(unit):
    info = specs[unit]
    print(unit)
    if 'cmd' in info:
        print(f'cmd: {info["cmd"]}')
    if 'dir' in info:
        print(f'dir: {info["dir"]}')
    if is_running(unit):
        print(f'status: running')
    else:
        print(f'status: not running')
    print()

def do_status(unit):
    if is_running(unit):
        print(f'{unit}: running')
    else:
        print(f'{unit}: not running')

def do_start(unit, *args):
    # get unit status
    info = specs[unit]
    if is_running(unit):
        print(f'{unit}: already running')
        return

    # check working directory
    pwd = info['dir']
    if not os.path.isdir(pwd):
        print(f'{unit}: working directory ({pwd}) does not exist')
        return

    # get session command
    env = info.get('env', None)
    cmd0 = ' '.join([info['cmd'], *args])

    # start session
    print(f'{unit}: starting with args = {args}')
    session = server.new_session(
        session_name=unit,
        start_directory=pwd,
        window_command=cmd0,
        environment=env,
        attach=False,
    )

    # set up logging
    pane = session.active_window.active_pane
    pane.cmd('pipe-pane', f'cat >> {pwd}/{unit}.log')

def do_stop(unit):
    session = get_session(unit)
    if session is None:
        print(f'{unit}: not running')
    else:
        print(f'{unit}: stopping')
        session.kill()

def do_restart(unit, *args):
    if is_running(unit):
        do_stop(unit)
    do_start(unit, *args)

def do_attach(unit):
    session = get_session(unit)
    if session is None:
        print(f'{unit}: not running')
        return
    session.cmd('attach', '-r')

def do_log(unit):
    info = specs[unit]
    pwd = info['dir']
    if not os.path.isdir(pwd):
        print(f'{unit}: working directory ({pwd}) does not exist')
        return
    os.system(f'cat {pwd}/{unit}.log')

def do_tail(unit):
    info = specs[unit]
    pwd = info['dir']
    if not os.path.isdir(pwd):
        print(f'{unit}: working directory ({pwd}) does not exist')
        return
    os.system(f'tail -f {pwd}/{unit}.log')

# interface
class Mrv:
    def list(self):
        print(', '.join(specs.keys()))

    def info(self, unit=None):
        dispatch(do_info, unit)

    def status(self, unit=None):
        dispatch(do_status, unit)

    def start(self, unit=None, *args):
        dispatch(do_start, unit, *args)

    def stop(self, unit=None):
        dispatch(do_stop, unit)

    def restart(self, unit=None, *args):
        dispatch(do_restart, unit, *args)

    def attach(self, unit):
        do_attach(unit)

    def log(self, unit):
        do_log(unit)

    def tail(self, unit):
        do_tail(unit)

def main():
    fire.Fire(Mrv)

if __name__ == '__main__':
    main()

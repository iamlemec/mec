#!/usr/bin/env python

import os
import tomllib
import fire
import libtmux

from .reg import CONFIG_DIR

# get specification
with (CONFIG_DIR / 'mux.toml').open('rb') as fid:
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

def do_stat(unit):
    if is_running(unit):
        print(f'{unit}: running')
    else:
        print(f'{unit}: not running')

def do_start(unit, *args):
    info = specs[unit]
    if is_running(unit):
        print(f'{unit}: already running')
        return
    pwd = info['dir']
    if not os.path.isdir(pwd):
        print(f'{unit}: working directory ({pwd}) does not exist')
        return
    env = info.get('env', None)
    cmd0 = ' '.join([info['cmd'], *args])
    print(f'{unit}: starting with args = {args}')
    server.new_session(
        session_name=unit,
        start_directory=pwd,
        window_command=cmd0,
        environment=env,
        attach=False,
    )

def do_kill(unit):
    session = get_session(unit)
    if session is None:
        print(f'{unit}: not running')
    else:
        print(f'{unit}: killing')
        session.kill()

def do_restart(unit, *args):
    if is_running(unit):
        do_kill(unit)
    do_start(unit, *args)

# interface
class Mux:
    def list(self):
        print(', '.join(specs.keys()))

    def info(self, unit=None):
        dispatch(do_info, unit)

    def stat(self, unit=None):
        dispatch(do_stat, unit)

    def status(self, unit=None):
        dispatch(do_stat, unit)

    def start(self, unit=None, *args):
        dispatch(do_start, unit, *args)

    def kill(self, unit=None):
        dispatch(do_kill, unit)

    def stop(self, unit=None):
        dispatch(do_kill, unit)

    def restart(self, unit=None, *args):
        dispatch(do_restart, unit, *args)

    def log(self, unit):
        session = get_session(unit)
        if session is None:
            print(f'{unit}: not running')
            return
        pane = session.active_window.active_pane
        output = pane.capture_pane(start='-')
        print('\n'.join(output))

    def tail(self, unit, n=10, f=False):
        session = get_session(unit)
        if session is None:
            print(f'{unit}: not running')
            return
        if f:
            os.system(f'tmux attach -r -t {unit}')
        else:
            pane = session.active_window.active_pane
            output = pane.capture_pane(start='-')
            for line in output[-n:]:
                print(line)

def main():
    fire.Fire(Mux)

if __name__ == '__main__':
    main()

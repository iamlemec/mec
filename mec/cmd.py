# something like commandlets

import os
import fire
import inspect

from inspect import Parameter

from .reg import COMMANDS

##
## load commands
##

# get xdg config home
xdg_config_home = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
cmd_path = os.path.join(xdg_config_home, 'mec', 'mec.py')

# load commands
with open(cmd_path) as fid:
    code = fid.read()
    exec(code)

##
## command router
##

# try to give helpful error messages
def validate(cmd: str, *args, **kwargs) -> bool:
    # get function signature
    func = COMMANDS[cmd]
    sig = inspect.signature(func)

    # collect required and optional arguments
    reqs = [ k for k, v in sig.parameters.items() if v.default == Parameter.empty ]
    opts = [ k for k, v in sig.parameters.items() if v.default != Parameter.empty ]

    # check positional arguments
    if len(args) != len(reqs):
        print(f"Invalid number of positional arguments: got {len(args)}, expected {len(reqs)} ({', '.join(reqs)})")
        return False

    # check keyword arguments
    unknown = []
    for k in kwargs:
        if k not in opts:
            unknown.append(k)
    if len(unknown) > 0:
        names = [ f'--{k}' for k in unknown ]
        print(f"Unknown keyword arguments: {', '.join(names)}")
        return False

    # success
    return True

# dispatch command
def dispatch(cmd, *args, **kwargs) -> None:
    if validate(cmd, *args, **kwargs):
        COMMANDS[cmd](*args, **kwargs)

##
## main entry point
##

# entry point
def main() -> None:
    fire.Fire(dispatch)

# fire up the CLI
if __name__ == '__main__':
    main()

# something like commandlets

import sys
import fire
import inspect
from typing import Any
from inspect import Parameter

from .reg import COMMANDS, CONFIG_DIR, Stdin

##
## load commands
##

with (CONFIG_DIR / 'cmd.py').open() as fid:
    code = fid.read()
    exec(code)

##
## command router
##

def is_required(param: Parameter) -> bool:
    return param.default is Parameter.empty

def is_optional(param: Parameter) -> bool:
    return param.default is not Parameter.empty

def read_stdin() -> str:
    return sys.stdin.read()[:-1]

def splice_stdin(params: list[Parameter], args: list[Any]) -> list[Any]:
    i = 0
    args1 = []
    for par in params:
        if par.annotation is Stdin:
            args1.append(read_stdin())
        else:
            args1.append(args[i])
            i += 1
    args1.extend(args[i:])
    return args1

# try to give helpful error messages
def validate(cmd: str, *args, **kwargs) -> bool:
    # get function signature
    func = COMMANDS[cmd]
    sig = inspect.signature(func)
    par = sig.parameters

    # collect required and optional arguments
    reqs = { k: v for k, v in par.items() if is_required(v) }
    opts = { k: v for k, v in par.items() if is_optional(v) }

    # fill in stdin value
    args = splice_stdin(list(reqs.values()), args)

    # check positional arguments
    if len(args) != len(reqs):
        print(f"Invalid number of positional arguments: got {len(args)}, expected {len(reqs)} ({', '.join(reqs)})")
        return

    # check keyword arguments
    unknown = []
    for k in kwargs:
        if k not in opts:
            unknown.append(k)
    if len(unknown) > 0:
        names = [ f'--{k}' for k in unknown ]
        print(f"Unknown keyword arguments: {', '.join(names)}")
        return

    # success
    return args, kwargs

# dispatch command
def run(cmd, *args, **kwargs) -> str | None:
    if (ret := validate(cmd, *args, **kwargs)) is None:
        return
    args1, kwargs1 = ret
    return COMMANDS[cmd](*args1, **kwargs1)

##
## main entry point
##

# entry point
def main() -> None:
    fire.Fire(run)

# fire up the CLI
if __name__ == '__main__':
    main()

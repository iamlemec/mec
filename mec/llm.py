# llm tools

from inspect import signature
from mimetypes import guess_type
from typing import Any, Callable, Type
from pydantic_ai import Agent, BinaryContent

from .reg import CONFIG as C

type Image = BinaryContent | str
type Processor = Callable[[Any, Type], Any]

def params_processor(func: Callable, process: Processor) -> Callable:
    sig = signature(func)
    dtyp = { k: v.annotation for k, v in sig.parameters.items() }
    ltyp = list(dtyp.values())
    def processor(*args, **kwargs):
        args1 = [ process(a, ltyp[i]) for i, a in enumerate(args) ]
        kwargs1 = { k: process(a, dtyp[k]) for k, a in kwargs.items() }
        return func(*args1, **kwargs1)
    return processor

def convert_image(image: Image) -> BinaryContent:
    if isinstance(image, str):
        with open(image, 'rb') as fid:
            data = fid.read()
        mime, _ = guess_type(image)
        return BinaryContent(data=data, media_type=mime)
    return image

def convert_param(value: Any, type: Type) -> Any:
    if type is Image:
        return convert_image(value)
    return value

# decorator convert image types to message parts
def llm(func: Callable) -> Callable:
    proc = params_processor(func, convert_param)
    def wrapper(*args, **kwargs):
        # get processed message parts
        parts = proc(*args, **kwargs)

        # generate llm response
        agent = Agent(C.model)
        result = agent.run_sync(parts)
        response = result.output

        # return response
        return response
    return wrapper

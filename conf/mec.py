from mec import register, CONFIG as C

from mimetypes import guess_type
from pydantic_ai import Agent, BinaryContent

##
## defaults
##

C.model = 'openai:gpt-5.2'

##
## commands
##

@register
def diff(
    repo: str = '.',
    prompt: str = 'Summarize the changes in this diff in a single sentence.',
) -> None:
    from git import Repo

    # get diff text
    repo = Repo(repo)
    diff = repo.git.diff()

    # summarize diff
    query = f'{prompt}\n\n{diff}'
    agent = Agent(C.model)
    result = agent.run_sync(query)
    summary = result.output

    # print summary
    print(summary)

@register
def image(
    path: str,
    prompt: str = 'Generate a description of this image.',
) -> None:
    # load image data
    with open(path, 'rb') as fid:
        data = fid.read()

    # create image part
    mime, _ = guess_type(path)
    image = BinaryContent(data=data, media_type=mime)

    # generate description
    agent = Agent(C.model)
    result = agent.run_sync([ prompt, image ])
    description = result.output

    # print description
    print(description)

from mec import register, llm, Image, Stdin

##
## commands
##

@register
@llm
def diff(
    repo: str = '.',
    prompt: str = 'Summarize the changes in this diff in a single sentence.',
):
    from git import Repo
    repo = Repo(repo)
    diff = repo.git.diff()
    return f'{prompt}\n\n{diff}'

@register
@llm
def image(
    image: Image,
    prompt: str = 'Generate a description of this image.',
):
    return [ prompt, image ]

@register
def echo(
    stdin: Stdin,
    reps: int = 1,
    join: str = ' ',
):
    return join.join([stdin] * reps)

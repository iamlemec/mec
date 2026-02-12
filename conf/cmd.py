from mec import register, llm, Image

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

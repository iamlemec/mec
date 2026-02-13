from mec import register, llm, Image, Stdin

@register
@llm
def diff(prompt: str = 'Summarize this diff in a single sentence:', repo: str = '.'):
    from git import Repo
    repo = Repo(repo)
    diff = repo.git.diff()
    return f'{prompt}\n\n{diff}'

@register
@llm
def image(image: Image, prompt: str = 'Describe this image:'):
    return [ prompt, image ]

@register
@llm
def code(code: Stdin, prompt: str = 'Explain this code:'):
    return f'{prompt}\n\n{code}'

@register
def echo(stdin: Stdin, reps: int = 1, join: str = ' '):
    return join.join([stdin] * reps)

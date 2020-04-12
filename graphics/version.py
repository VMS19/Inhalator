from sh import git

__version__ = git.describe(tags=True, dirty=True)

import sh

try:
    __version__ = sh.git.describe(tags=True, dirty=True, abbrev=0)
except sh.ErrorReturnCode_128:
    __version__ = "Cannot read version!"

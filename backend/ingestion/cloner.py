"""
Judd Ebert 3/15/2026
Clones a github repository from a link
"""

from git import Repo
import tempfile

def clone_repo(url: str):
    temp_dir = tempfile.mkdtemp
    Repo.clone_from(url, temp_dir)
    return temp_dir
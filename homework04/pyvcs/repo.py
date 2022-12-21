import os
import pathlib
import typing as tp


def repo_find(workdir: tp.Union[str, pathlib.Path] = ".") -> pathlib.Path:
    workdir = pathlib.Path(workdir)
    if os.environ.get("GIT_DIR"):
        git_dir = os.environ["GIT_DIR"]
    else:
        git_dir = ".git"
    path = workdir / git_dir
    if path.exists():
        return path
    else:
        for i in path.parents:
            if i.name == git_dir:
                return i
        raise Exception("Not a git repository")


def repo_create(workdir: tp.Union[str, pathlib.Path]) -> pathlib.Path:
    workdir = pathlib.Path(workdir)
    if not workdir.is_dir():
        raise Exception(f"{workdir.name} is not a directory")
    if os.environ.get("GIT_DIR"):
        git_dir = os.environ["GIT_DIR"]
    else:
        git_dir = ".git"
    path = workdir / git_dir
    path.mkdir()
    (path / "refs").mkdir()
    (path / "refs/heads").mkdir()
    (path / "refs/tags").mkdir()
    (path / "objects").mkdir()
    with open(path / "HEAD", "w") as head:
        head.write("ref: refs/heads/master\n")
    with open(path / "config", "w") as config:
        config.write(
            "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = false\n"
        )
    with open(path / "description", "w") as description:
        description.write("Unnamed pyvcs repository.\n")
    return path
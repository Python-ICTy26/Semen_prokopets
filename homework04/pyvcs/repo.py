import os
import pathlib
import typing as tp


def repo_find(workdir: tp.Union[str, pathlib.Path] = ".") -> pathlib.Path:
    git_dir = os.getenv("GIT_DIR", ".pyvcs")
    workdir = pathlib.Path(workdir)
    while workdir.absolute() != pathlib.Path(workdir.absolute().root):
        if (workdir / git_dir).exists():
            return workdir / git_dir
        workdir = workdir.parent
    if (workdir / git_dir).exists():
        return workdir / git_dir
    raise Exception("Not a git repository")


def repo_create(workdir: tp.Union[str, pathlib.Path]) -> pathlib.Path:
    git_dir = os.getenv("GIT_DIR", ".pyvcs")
    workdir = pathlib.Path(workdir)
    if workdir.is_dir():
        os.mkdir(workdir / git_dir)
        os.mkdir(workdir / git_dir / "objects")
        os.mkdir(workdir / git_dir / "refs")
        os.mkdir(workdir / git_dir / "refs" / "heads")
        os.mkdir(workdir / git_dir / "refs" / "tags")
        with open(workdir / git_dir / "HEAD", "w") as f:
            f.write("ref: refs/heads/master\n")
        with open(workdir / git_dir / "config", "w") as f:
            f.write(
                "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = false\n"
            )
        with open(workdir / git_dir / "description", "w") as f:
            f.write("Unnamed pyvcs repository.\n")
        return workdir / git_dir
    raise Exception(f"{workdir} is not a directory")

import os
import pathlib
import shutil
import typing as tp

from pyvcs.index import read_index, update_index
from pyvcs.objects import commit_parse, find_object, find_tree_files, read_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref
from pyvcs.tree import commit_tree, write_tree


def add(gitdir: pathlib.Path, paths: tp.List[pathlib.Path]) -> None:
    update_index(gitdir, paths)


def commit(gitdir: pathlib.Path, message: str, author: tp.Optional[str] = None) -> str:
    index = read_index(gitdir)
    return commit_tree(
        gitdir=gitdir, tree=write_tree(gitdir, index), message=message, author=author
    )


def checkout(gitdir: pathlib.Path, obj_name: str) -> None:
    head = gitdir / "refs" / "heads" / obj_name
    if head.exists():
        with head.open("r") as f:
            obj_name = f.read()
    index = read_index(gitdir)
    for i in index:
        if pathlib.Path(i.name).is_file():
            if "/" in i.name:
                shutil.rmtree(i.name[: i.name.find("/")])
            else:
                os.chmod(i.name, 0o777)
                os.remove(i.name)
    obj_path = gitdir / "objects" / obj_name[:2] / obj_name[2:]
    with obj_path.open("rb") as f:
        com = f.read()
    for j in find_tree_files(commit_parse(com).decode(), gitdir):
        if "/" in j[0]:
            dir_name = j[0][: j[0].find("/")]
            pathlib.Path(dir_name).absolute().mkdir()

        with open(j[0], "w") as file:
            header, content = read_object(j[1], gitdir)
            file.write(content.decode())
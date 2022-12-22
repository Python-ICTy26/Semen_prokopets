import os
import pathlib
import typing as tp

from pyvcs.index import read_index, update_index
from pyvcs.objects import commit_parse, find_object, find_tree_files, read_object, read_tree
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref
from pyvcs.tree import commit_tree, write_tree


def add(gitdir: pathlib.Path, paths: tp.List[pathlib.Path]) -> None:
    update_index(gitdir, list(filter(lambda x: x.is_file(), paths)), write=True)
    for path in filter(lambda x: x.is_dir(), paths):
        add(gitdir, [x for x in path.glob("*")])


def commit(gitdir: pathlib.Path, message: str, author: tp.Optional[str] = None) -> str:
    tree = write_tree(gitdir, read_index(gitdir), str(gitdir.parent))
    parent_commit = resolve_head(gitdir)
    commit_hash = commit_tree(gitdir, tree, message, parent_commit, author)
    return commit_hash


def checkout(gitdir: pathlib.Path, obj_name: str) -> None:
    for entry in read_index(gitdir):
        try:
            os.remove(gitdir.parent / entry.name)
        except FileNotFoundError:
            pass
    commit_data = commit_parse(read_object(obj_name, gitdir)[1])
    done = False
    while not done:
        trees: tp.List[tp.Tuple[pathlib.Path, tp.List[tp.Tuple[int, str, str]]]] = [
            (gitdir.parent, read_tree(read_object(commit_data["tree"], gitdir)[1]))
        ]
        while len(trees) != 0:
            tree_path, tree_content = trees.pop()
            for file_data in tree_content:
                fmt, data = read_object(file_data[2], gitdir)
                if fmt == "tree":
                    trees.append((tree_path / file_data[1], read_tree(data)))
                    try:
                        (tree_path / file_data[1]).mkdir()
                    except FileExistsError:
                        pass
                else:
                    if not (tree_path / file_data[1]).exists():
                        with (tree_path / file_data[1]).open("wb") as f:
                            f.write(data)
                        (tree_path / file_data[1]).chmod(file_data[0])
            if "parent" in commit_data:
                commit_data = commit_parse((read_object(commit_data["parent"], gitdir)[1]))
            else:
                done = True
    for dir in filter(lambda x: x != gitdir and x.is_dir(), gitdir.parent.glob("*")):
        try:
            os.removedirs(dir)
        except OSError:
            pass

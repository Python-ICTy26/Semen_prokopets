import os
import pathlib
import stat
import time
import typing as tp

from pyvcs.index import GitIndexEntry, read_index
from pyvcs.objects import hash_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref


def write_tree(gitdir: pathlib.Path, index: tp.List[GitIndexEntry], dirname: str = "") -> str:
    path = gitdir.parent / dirname
    (*files,) = map(lambda x: str(x), path.glob("*"))
    subdirs: tp.Dict[str, tp.List[GitIndexEntry]] = dict()
    main_content: tp.List[tp.Tuple[int, bytes, str]] = []
    for entry in index:
        if entry.name in files:
            main_content.append((entry.mode, entry.sha1, pathlib.Path(entry.name).name))
        else:
            dir_name = entry.name.strip(dirname).split("/")[0]
            if not dir_name in subdirs:
                subdirs[dir_name] = []
            subdirs[dir_name].append(entry)
    for dir_name in subdirs:
        if dirname == "":
            main_content.append(
                (0o40000, bytes.fromhex(write_tree(gitdir, subdirs[dir_name], dir_name)), dir_name)
            )
        else:
            main_content.append(
                (
                    0o40000,
                    bytes.fromhex(write_tree(gitdir, subdirs[dir_name], dirname + "/" + dir_name)),
                    dirname + "/" + dir_name,
                )
            )
    data = b""
    main_content = sorted(main_content, key=lambda x: x[2])
    for content in main_content:
        data += (str(oct(content[0])[2:]) + " " + content[2]).encode() + b"\00" + content[1]
    return hash_object(data, "tree", write=True)


def commit_tree(
    gitdir: pathlib.Path,
    tree: str,
    message: str,
    parent: tp.Optional[str] = None,
    author: tp.Optional[str] = None,
) -> str:
    if author is None and "GIT_AUTHOR_NAME" in os.environ and "GIT_AUTHOR_EMAIL" in os.environ:
        author = (
            os.getenv("GIT_AUTHOR_NAME", None)  # type:ignore
            + " "  # type:ignore
            + f'<{os.getenv("GIT_AUTHOR_EMAIL", None)}>'  # type:ignore
        )  # type:ignore
    timezone_int = time.timezone
    if timezone_int > 0:
        timezone_str = "-" + f"{abs(timezone_int) // 3600:02}{abs(timezone_int) // 60 % 60:02}"
    else:
        timezone_str = "+" + f"{abs(timezone_int) // 3600:02}{abs(timezone_int) // 60 % 60:02}"
    commit = []
    commit.append(f"tree {tree}")
    if parent is not None:
        commit.append(f"parent {parent}")
    commit.append(f"author {author} {int(time.mktime(time.localtime()))} {timezone_str}")
    commit.append(f"committer {author} {int(time.mktime(time.localtime()))} {timezone_str}")
    commit.append(f"\n{message}\n")
    data = "\n".join(commit).encode()
    return hash_object(data, "commit", write=True)

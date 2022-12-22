import os
import pathlib
import stat
import time
import typing as tp

from pyvcs.index import GitIndexEntry, read_index
from pyvcs.objects import hash_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref


def write_tree(gitdir: pathlib.Path, index: tp.List[GitIndexEntry], dirname: str = "") -> str:
    data = b""

    for file in index:
        if "/" in file.name:
            s = file.name.find("/")
            directory = file.name[:s].encode()
            mode = oct(file.mode)[2:].encode()
            child = (
                b""
                + mode
                + b" "
                + file.name[file.name.find("/") + 1 :].encode()
                + b"\0"
                + file.sha1
            )
            hash = bytes.fromhex(hash_object(child, "tree", True))
            data += b"40000 " + directory + b"\0" + hash
        else:
            data += oct(file.mode)[2:].encode() + b" " + file.name.encode() + b"\0" + file.sha1

    return hash_object(data, fmt="tree", write=True)


def commit_tree(
    gitdir: pathlib.Path,
    tree: str,
    message: str,
    parent: tp.Optional[str] = None,
    author: tp.Optional[str] = None,
) -> str:
    zone = time.timezone
    offset = "+" if zone < 0 else "-"
    zone = abs(zone)
    zone = zone // 60
    offset += f"{zone // 60:02}"
    offset += f"{zone % 60:02}"

    local = time.localtime()
    sec = time.mktime(local)
    sec = int(sec)

    if not author:
        author = f"{os.getenv('GIT_AUTHOR_NAME')} <{os.getenv('GIT_AUTHOR_EMAIL')}>"

    dt = [f"tree {tree}"]

    if parent:
        dt.append(f"parent {parent}")

    dt.extend(
        [f"author {author} {sec} {offset}", f"committer {author} {sec} {offset}", f"\n{message}\n"]
    )
    string = "\n".join(dt)

    return hash_object(string.encode(), "commit", True)

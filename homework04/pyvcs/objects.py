import hashlib
import os
import pathlib
import re
import stat
import typing as tp
import zlib

from pyvcs.refs import update_ref
from pyvcs.repo import repo_find


def hash_object(data: bytes, fmt: str, write: bool = False) -> str:
    root = ".git"

    header = f"{fmt} {len(data)}\0"
    store = header.encode() + data
    hash = hashlib.sha1(store).hexdigest()

    if not write:
        return hash

    path = root + "/objects/" + hash[:2]
    if not os.path.exists(path):
        os.makedirs(path)

    with open(path + os.sep + hash[2:], "wb") as f:
        f.write(zlib.compress(store))

    return hash


def resolve_object(obj_name: str, gitdir: pathlib.Path) -> tp.List[str]:
    if not 4 <= len(obj_name) <= 40:
        raise Exception(f"Not a valid object name {obj_name}")
    objs_path = gitdir / "objects" / obj_name[:2]
    objects = []
    for obj_path in objs_path.iterdir():
        if not obj_path.name.find(obj_name[2:]):
            objects.append(obj_name[:2] + obj_path.name)
    if len(objects):
        return objects
    else:
        raise Exception(f"Not a valid object name {obj_name}")


def find_object(obj_name: str, gitdir: pathlib.Path) -> tp.Optional[str]:
    if obj_name[2:] in gitdir.parts[-1]:
        return f"{gitdir.parts[-2]}{gitdir.parts[-1]}"
    else:
        return None


def read_object(sha: str, gitdir: pathlib.Path) -> tp.Tuple[str, bytes]:
    path = gitdir / "objects" / sha[:2] / sha[2:]
    with open(path, mode="rb") as f:
        obj_data = zlib.decompress(f.read())
    h = obj_data.find(b"\x00")
    header = obj_data[:h]
    b = obj_data.find(b" ")
    fmt = header[:b].decode("ascii")
    content_len = int(header[b:h].decode("ascii"))
    content = obj_data[h + 1 :]
    assert content_len == len(content)
    return (fmt, content)


def read_tree(data: bytes) -> tp.List[tp.Tuple[int, str, str]]:
    result = []
    while len(data) != 0:
        b = data.find(b" ")
        fmt = int(data[:b].decode())
        data = data[b + 1 :]
        ln = data.find(b"\x00")
        length = data[:ln].decode()
        data = data[ln + 1 :]
        sha = bytes.hex(data[:20])
        data = data[20:]
        result.append((fmt, length, sha))
    return result


def cat_file(obj_name: str, pretty: bool = True) -> None:
    gitdir = repo_find()

    for obj in resolve_object(obj_name, gitdir):
        header, content = read_object(obj, gitdir)
        if header == "tree":
            result = ""
            tree_files = read_tree(content)
            for f in tree_files:
                object_type = read_object(f[2], pathlib.Path(".git"))[0]
                result += str(f[0]).zfill(6) + " "
                result += object_type + " "
                result += f[2] + "\t"
                result += f[1] + "\n"
            print(result)
        else:
            print(content.decode())


def find_tree_files(tree_sha: str, gitdir: pathlib.Path) -> tp.List[tp.Tuple[str, str]]:
    result = []
    header, data = read_object(tree_sha, gitdir)
    for f in read_tree(data):
        if read_object(f[2], gitdir)[0] == "tree":
            tree = find_tree_files(f[2], gitdir)
            for blob in tree:
                name = f[1] + "/" + blob[0]
                result.append((name, blob[1]))
        else:
            result.append((f[1], f[2]))
    return result


def commit_parse(raw: bytes, start: int = 0, dct=None):
    data = zlib.decompress(raw)
    i = data.find(b"tree")
    return data[i + 5 : i + 45]

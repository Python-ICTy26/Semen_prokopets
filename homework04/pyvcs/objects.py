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
    data = f"{fmt} {len(data)}\0".encode() + data
    hashed_object = hashlib.sha1(data)
    hex_dig = hashed_object.hexdigest()
    if write:
        gitdir = repo_find()
        if not (gitdir / "objects" / hex_dig[:2]).exists():
            os.mkdir(gitdir / "objects" / hex_dig[:2])
        with open(gitdir / "objects" / hex_dig[:2] / hex_dig[2:], mode="wb") as f:
            f.write(zlib.compress(data))
    return hex_dig


def resolve_object(obj_name: str, gitdir: pathlib.Path) -> tp.List[str]:
    if len(obj_name) < 4:
        raise Exception(f"Not a valid object name {obj_name}")
    result = []
    for path in (gitdir / "objects" / obj_name[:2]).glob(obj_name[2:] + "*"):
        result.append(obj_name[:2] + path.name)
    if result:
        return result
    raise Exception(f"Not a valid object name {obj_name}")


def find_object(obj_name: str, gitdir: pathlib.Path) -> str:
    # PUT YOUR CODE HERE
    ...


def read_object(sha: str, gitdir: pathlib.Path) -> tp.Tuple[str, bytes]:
    with open(gitdir / "objects" / sha[:2] / sha[2:], mode="rb") as f:
        data = zlib.decompress(f.read())
    header, main_data = data.split(b"\00", maxsplit=1)
    return header.split(b" ")[0].decode(), main_data


def read_tree(data: bytes) -> tp.List[tp.Tuple[int, str, str]]:
    result = []
    while data:
        before_sha_ind = data.index(b"\00")
        result.append(
            (
                int(data[:before_sha_ind].decode().split(" ")[0]),
                data[:before_sha_ind].decode().split(" ")[1],
                data[before_sha_ind + 1 : before_sha_ind + 21].hex(),
            )
        )
        data = data[before_sha_ind + 21 :]
    return result


def cat_file(obj_name: str, pretty: bool = True) -> None:
    fmt, data = read_object(obj_name, repo_find())
    if fmt == "tree":
        for i in read_tree(data):
            if i[0] == 40000:
                print(f"{i[0]:06} tree {i[2]}\t{i[1]}")
            else:
                print(f"{i[0]:06} blob {i[2]}\t{i[1]}")
    else:
        print(data.decode())


def find_tree_files(tree_sha: str, gitdir: pathlib.Path) -> tp.List[tp.Tuple[str, str]]:
    # PUT YOUR CODE HERE
    ...


def commit_parse(raw: bytes, start: int = 0, dct=None):
    data: tp.Dict[str, tp.Any] = {"message": []}
    for line in raw.decode().split("\n"):
        if line.startswith(("tree", "parent", "author", "committer")):
            name, val = line.split(" ", maxsplit=1)
            data[name] = val
        else:
            data["message"].append(line)
    return data

import hashlib
import operator
import os
import pathlib
import struct
import typing as tp

from pyvcs.objects import hash_object


class GitIndexEntry(tp.NamedTuple):
    # @see: https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
    ctime_s: int
    ctime_n: int
    mtime_s: int
    mtime_n: int
    dev: int
    ino: int
    mode: int
    uid: int
    gid: int
    size: int
    sha1: bytes
    flags: int
    name: str

    def pack(self) -> bytes:
        return struct.pack(
            f"!10I20sH{len(self.name)}s{8 - (62 + len(self.name)) % 8}x",
            self.ctime_s,
            self.ctime_n,
            self.mtime_s,
            self.mtime_n,
            self.dev,
            self.ino & 0xFFFFFFFF,
            self.mode,
            self.uid,
            self.gid,
            self.size,
            self.sha1,
            self.flags,
            self.name.encode(),
        )

    @staticmethod
    def unpack(data: bytes) -> "GitIndexEntry":
        information = [x for x in struct.unpack(f"!10I20sH{len(data) - 62}s", data)]
        information[-1] = information[-1].strip(b"\x00").decode()
        return GitIndexEntry(*information)


def read_index(gitdir: pathlib.Path) -> tp.List[GitIndexEntry]:
    if not (gitdir / "index").exists():
        return []
    with (gitdir / "index").open("rb") as f:
        data = f.read()
    count = struct.unpack(">I", data[8:12])[0]
    prev_pos = 12
    entries = []
    for i in range(count):
        new_pos = data.find(b"\x00", prev_pos + 62)
        if data[new_pos - 1] != 0:
            new_pos += 1
        while (new_pos - 12) % 8 != 0:
            new_pos += 1
        entries.append(GitIndexEntry.unpack(data[prev_pos:new_pos]))
        prev_pos = new_pos
    return entries


def write_index(gitdir: pathlib.Path, entries: tp.List[GitIndexEntry]) -> None:
    data = b"DIRC"
    data += struct.pack("!2I", 2, len(entries))
    entries.sort(key=lambda x: x.name)
    for entry in entries:
        data += entry.pack()
    with open(gitdir / "index", "wb") as f:
        f.write(data + hashlib.sha1(data).digest())


def ls_files(gitdir: pathlib.Path, details: bool = False) -> None:
    index = read_index(gitdir)
    for entry in index:
        if details:
            print(f"{entry.mode:o} {entry.sha1.hex()} 0\t{entry.name}")
        else:
            print(entry.name)


def update_index(gitdir: pathlib.Path, paths: tp.List[pathlib.Path], write: bool = True) -> None:
    entries = read_index(gitdir)
    for path in paths:
        with open(path, "rb") as f:
            data = f.read()
        stat = path.stat()
        entries.append(
            GitIndexEntry(
                int(stat.st_ctime),
                0,
                int(stat.st_mtime),
                0,
                stat.st_dev,
                stat.st_ino,
                stat.st_mode,
                stat.st_uid,
                stat.st_gid,
                stat.st_size,
                bytes.fromhex(hash_object(data, "blob", True)),
                len(path.name),
                str(path),
            )
        )
    if write:
        write_index(gitdir, entries)

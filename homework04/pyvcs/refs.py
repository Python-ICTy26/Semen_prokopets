import pathlib
import typing as tp


def update_ref(gitdir: pathlib.Path, ref: tp.Union[str, pathlib.Path], new_value: str) -> None:
    refpath = gitdir / pathlib.Path(ref)
    with refpath.open("w") as f:
        f.write(new_value)


def symbolic_ref(gitdir: pathlib.Path, name: str, ref: str) -> None:
    if ref_resolve(gitdir, ref) is None:
        return None
    with (gitdir / name).open("w") as f:
        f.write(f"ref: {ref}")


def ref_resolve(gitdir: pathlib.Path, refname: str) -> tp.Optional[str]:
    if refname == "HEAD":
        refname = get_ref(gitdir)
    if not (gitdir / refname).exists():
        return None
    with open((gitdir / refname), "r") as f:
        out = f.read()
    return out


def resolve_head(gitdir: pathlib.Path) -> tp.Optional[str]:
    return ref_resolve(gitdir, "HEAD")


def is_detached(gitdir: pathlib.Path) -> bool:
    with (gitdir / "HEAD").open("r") as f:
        chref = str(f.read())
    if chref.find("ref") == -1:
        return True
    return False


def get_ref(gitdir: pathlib.Path) -> str:
    with open((gitdir / "HEAD"), "r") as f:
        gref = f.read()
    return gref[gref.find(" ") + 1 :].strip()
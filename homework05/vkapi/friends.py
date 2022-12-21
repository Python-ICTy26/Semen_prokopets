import dataclasses
import math
import time
import typing as tp

from vkapi import session
from vkapi.config import VK_CONFIG
from vkapi.exceptions import APIError

QueryParams = tp.Optional[tp.Dict[str, tp.Union[str, int]]]


@dataclasses.dataclass(frozen=True)
class FriendsResponse:
    count: int
    items: tp.Union[tp.List[int], tp.List[tp.Dict[str, tp.Any]]]


def get_friends(
    user_id: int, count: int = 5000, offset: int = 0, fields: tp.Optional[tp.List[str]] = None
) -> FriendsResponse:
    response = session.get(
        "friends.get",
        user_id=user_id,
        count=count,
        fields=fields,
        offset=offset,
        access_token=VK_CONFIG["access_token"],
        v=VK_CONFIG["version"],
    )

    json = response.json()["response"]
    return FriendsResponse(**json)


class MutualFriends(tp.TypedDict):
    id: int
    common_friends: tp.List[int]
    common_count: int


def get_mutual(
    source_uid: tp.Optional[int] = None,
    target_uid: tp.Optional[int] = None,
    target_uids: tp.Optional[tp.List[int]] = None,
    order: str = "",
    count: tp.Optional[int] = None,
    offset: int = 0,
    progress=None,
) -> tp.List[MutualFriends]:
    friends = []

    if target_uids is None:
        ln = 1
    else:
        ln = math.ceil(len(target_uids) / 100)

    params = {
        "source_uid": source_uid,
        "target_uid": target_uid,
        "target_uids": target_uids,
        "order": order,
        "count": count,
        "progress": progress,
    }

    for iter in range(ln):
        params["offset"] = iter * 100
        get = session.get(
            "friends.getMutual",
            **params,
        )
        response = get.json()["response"]
        friends += response

        time.sleep(1)

    return friends

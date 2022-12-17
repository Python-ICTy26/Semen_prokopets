import dataclasses
import math
import time
import typing as tp

import requests
from requests import get

from vkapi import config, session
from vkapi.exceptions import APIError

QueryParams = tp.Optional[tp.Dict[str, tp.Union[str, int]]]


@dataclasses.dataclass(frozen=True)
class FriendsResponse:
    count: int
    items: tp.Union[tp.List[int], tp.List[tp.Dict[str, tp.Any]]]


def get_friends(
    user_id: int, count: int = 5000, offset: int = 0, fields: tp.Optional[tp.List[str]] = None
) -> FriendsResponse:
    """
    Получить список идентификаторов друзей пользователя или расширенную информацию
    о друзьях пользователя (при использовании параметра fields).

    :param user_id: Идентификатор пользователя, список друзей для которого нужно получить.
    :param count: Количество друзей, которое нужно вернуть.
    :param offset: Смещение, необходимое для выборки определенного подмножества друзей.
    :param fields: Список полей, которые нужно получить для каждого пользователя.
    :return: Список идентификаторов друзей пользователя или список пользователей.
    """

    if fields is None:
        fields = []
    access_token = config.VK_CONFIG.get("access_token")
    v = config.VK_CONFIG.get("version")
    params = {
        "access_token": access_token,
        "user_id": user_id,
        "count": count,
        "fields": ",".join(fields),
        "v": v,
    }
    response = session.get("/friends.get", params=params)
    r = response.json()
    if "error" in r:
        raise APIError(r["error"]["error_msg"])
    resp = FriendsResponse(count=r["response"]["count"], items=r["response"]["items"])

    return resp


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
) -> tp.Union[tp.List[int], tp.List[MutualFriends]]:
    """
    Получить список идентификаторов общих друзей между парой пользователей.

    :param source_uid: Идентификатор пользователя, чьи друзья пересекаются с друзьями пользователя с идентификатором target_uid.
    :param target_uid: Идентификатор пользователя, с которым необходимо искать общих друзей.
    :param target_uids: Cписок идентификаторов пользователей, с которыми необходимо искать общих друзей.
    :param order: Порядок, в котором нужно вернуть список общих друзей.
    :param count: Количество общих друзей, которое нужно вернуть.
    :param offset: Смещение, необходимое для выборки определенного подмножества общих друзей.
    :param progress: Callback для отображения прогресса.
    """
    access_token = config.VK_CONFIG.get("access_token")
    v = config.VK_CONFIG.get("version")
    source_uid_str = str(source_uid)
    result = []
    if source_uid is None:
        source_uid_str = ""
    count_str = str(count)
    if count is None:
        count_str = ""
    if target_uids is None:
        params = {
            "access_token": access_token,
            "source_id": source_uid_str,
            "target_uid": target_uid,
            "count": count_str,
            "order": order,
            "v": v,
        }
        response = session.get("/friends.getMutual", params=params)
        r = response.json()
        if "error" in r:
            raise APIError(r["error"]["error_msg"])
        return r["response"]
    if progress is None:
        progress = lambda x: x
    for j, i in progress(enumerate(range(offset, len(target_uids), 100))):
        params = {
            "access_token": access_token,
            "source_id": source_uid_str,
            "target_uids": ",".join(map(str, target_uids)),
            "count": count_str,
            "order": order,
            "offset": i,
            "v": v,
        }
        response = session.get("/friends.getMutual", params=params)
        r = response.json()
        if "error" in r:
            raise APIError(r["error"]["error_msg"])
        if j % 3 == 0:
            time.sleep(1)
        for item in r["response"]:
            result.append(
                MutualFriends(
                    id=item["id"],
                    common_friends=item["common_friends"],
                    common_count=item["common_count"],
                )
            )

    return result

import datetime as dt
import statistics
import typing as tp

from vkapi.friends import get_friends


def age_predict(user_id: int) -> tp.Optional[float]:
    """
    Наивный прогноз возраста пользователя по возрасту его друзей.

    Возраст считается как медиана среди возраста всех друзей пользователя

    :param user_id: Идентификатор пользователя.
    :return: Медианный возраст пользователя.
    """
    current = dt.datetime.now()
    response = get_friends(user_id, fields=["bdate"])
    ages = []
    friend: tp.Dict[str, tp.Any]
    for friend in response.items:  # type: ignore
        if "bdate" not in friend:
            continue
        bdate = friend["bdate"]
        if len(bdate) > 6:
            bdate_tuple = dt.datetime.strptime(bdate, "%d.%m.%Y").timetuple()
        else:
            continue
        if (current.month > bdate_tuple.tm_mon) or (
            current.month == bdate_tuple.tm_mon and current.day > bdate_tuple.tm_mday
        ):
            age = current.year - bdate_tuple.tm_year
        else:
            age = current.year - bdate_tuple.tm_year - 1
        ages.append(age)
    if not ages:
        return None
    else:
        return statistics.median(ages)

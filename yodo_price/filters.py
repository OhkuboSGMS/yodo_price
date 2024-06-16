from itertools import groupby


def unique_consecutive(lst: list, attr_name: str) -> list:
    """
    Filter unique consecutive elements from a list
    連続した値をフィルタリングする
    例: 入力[1, 1, 2, 3, 3, 3, 4, 5, 5] -> 出力[1, 2, 3, 4, 5]
    :param lst:
    :return:
    """

    def get_attr(obj):
        return getattr(obj, attr_name)

    return [next(group) for key, group in groupby(lst, key=get_attr)]

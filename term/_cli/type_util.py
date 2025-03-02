import typing as t


def is_collection(_type: t.Any):
    return t.get_origin(_type) in (list, t.Sequence)

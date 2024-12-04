import os
from tinydb import TinyDB


def get_db(name):
    path = os.path.join(os.path.dirname(__file__), f"../databases/{name}.json")
    return TinyDB(path)


def check_fields(items, keys, msg):
    for obj in items:
        _keys = set(keys)
        __keys = set(obj.keys())
        assert (
            _keys == __keys
        ), f"expect fields of {_keys} but get {__keys} in {msg}"


def type_check(var, _type, name):
    msg = f"expect {name} to be type {_type} but get {type(var)}"
    if isinstance(_type, list):
        assert isinstance(var, list) and all(
            isinstance(el, _type[0]) for el in var
        ), msg
    else:
        assert isinstance(var, _type), msg
        
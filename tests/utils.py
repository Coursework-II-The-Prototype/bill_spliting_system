def check_fields(items, keys, msg):
    for obj in items:
        _keys = set(keys)
        __keys = set(obj.keys())
        assert (
            _keys == __keys
        ), f"expect fields of {_keys} but get {__keys} in {msg}"


def type_check(var, _type, msg):
    if isinstance(_type, list):
        assert isinstance(var, list) and all(
            isinstance(el, str) for el in var
        ), msg
    else:
        assert isinstance(var, str), msg

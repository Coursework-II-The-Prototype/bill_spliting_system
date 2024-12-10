import os
from tinydb import TinyDB, Query
from cerberus import Validator

mock_dir = f"{os.path.dirname(__file__)}/databases"


def get_db(name):
    path = os.path.join(os.path.dirname(__file__), f"../databases/{name}.json")
    return TinyDB(path)


def check_db(db, schema):
    for i in db.all():
        assert Validator(
            schema, require_all=True, allow_unknown=False
        ).validate(i)


def update_db(db, obj, id):
    db.update(obj, Query().order_id == id)

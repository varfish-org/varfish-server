import json

import aldjemy.core
import aldjemy.table
import sqlalchemy


class Cache:
    metadata = None
    engine_set = False


def get_engine(alias="default", **kwargs):
    if not Cache.engine_set:
        Cache.engine_set = True
        aldjemy.core.Cache.engines = {}
    result = aldjemy.core.get_engine(alias, json_deserializer=json.loads, **kwargs)
    return result


# Cache value for metatadata
_METADATA = None


def get_meta():
    """Return global SQLAlchemy meta data"""
    if not Cache.metadata:
        Cache.metadata = sqlalchemy.MetaData()
        aldjemy.table.generate_tables(Cache.metadata)
    return Cache.metadata

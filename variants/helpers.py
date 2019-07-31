import aldjemy.core
from sqlalchemy import create_engine


#
# Patching aldjemy to prevent sqlalchemy from applying (de)serialization on JSON fields that psycopg2 already did.
#


def get_engine(alias="default", **kwargs):
    """This is the function aldjemy.core.get_engine, additionally accepting kwargs."""
    if alias not in aldjemy.core.Cache.engines:
        engine_string = aldjemy.core.get_engine_string(alias)
        # we have to use autocommit=True, because SQLAlchemy
        # is not aware of Django transactions
        if engine_string == "sqlite3":
            kwargs["native_datetime"] = True

        pool = aldjemy.core.DjangoPool(alias=alias, creator=None)
        aldjemy.core.Cache.engines[alias] = create_engine(
            aldjemy.core.get_connection_string(alias), pool=pool, **kwargs
        )
    return aldjemy.core.Cache.engines[alias]


#: The SQL Alchemy engine to use.
SQLALCHEMY_ENGINE = get_engine(
    json_serializer=lambda x: x, json_deserializer=lambda x: x
)  # Patch for aldjemy.core.get_engine()

# shared/utils/database.py
from neo4j import GraphDatabase
import redis
import os
from contextlib import contextmanager


class DatabaseConnection:
    _neo4j_instance = None
    _redis_instance = None

    @classmethod
    def get_neo4j(cls):
        if cls._neo4j_instance is None:
            cls._neo4j_instance = GraphDatabase.driver(
                os.getenv('NEO4J_URI', 'bolt://neo4j:7687'),
                auth=(
                    os.getenv('NEO4J_USER', 'neo4j'),
                    os.getenv('NEO4J_PASSWORD', 'password')
                )
            )
        return cls._neo4j_instance

    @classmethod
    def get_redis(cls):
        if cls._redis_instance is None:
            cls._redis_instance = redis.Redis(
                host=os.getenv('REDIS_HOST', 'redis'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                decode_responses=True
            )
        return cls._redis_instance


@contextmanager
def neo4j_transaction():
    driver = DatabaseConnection.get_neo4j()
    with driver.session() as session:
        with session.begin_transaction() as tx:
            yield tx






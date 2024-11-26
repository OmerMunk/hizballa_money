
from neo4j import GraphDatabase
import redis
neo4j_driver = None
redis_client = None

def init_neo4j():
    global neo4j_driver
    neo4j_driver = GraphDatabase.driver(
        "bolt://neo4j:7687",
        auth=("neo4j", "password")
    )
    return neo4j_driver


def init_redis():
    global redis_client
    redis_client = redis.Redis(
        host='redis',
        port=6379,
        decode_responses=True
    )
    return redis_client



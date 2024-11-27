from neo4j import GraphDatabase
import redis



def init_neo4j():
    neo4j_driver = GraphDatabase.driver(
        "bolt://neo4j:7687",
        auth=("neo4j", "password")
    )
    return neo4j_driver


def init_redis():
    redis_client = redis.Redis(
        host='redis',
        port=6379,
        decode_responses=True
    )
    return redis_client



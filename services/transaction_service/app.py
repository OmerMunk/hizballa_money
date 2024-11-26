from flask import Flask, jsonify
from neo4j import GraphDatabase
import redis

app = Flask(__name__)


neo4j_driver = GraphDatabase.driver(
    "bolt://neo4j:7687",
    auth=("neo4j", "password")
)

redis_client = redis.Redis(
    host='redis',
    port= 6379,
    decode_responses=True
)

@app.route('/api/v1/transaction', methods=['POST'])
def create_transaction():
    return jsonify({"message": "Transaction created"}), 200





if __name__ == "__main__":
    print("Running the transaction service flask app")
    app.run(host='0.0.0.0', port=5001, debug=True)
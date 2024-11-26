from flask import Flask, jsonify
from neo4j import GraphDatabase
import redis




"""
how does the transaction node look?
מי שילם
למי היא שילם
כמה הוא שילם
תאריך של התשלום
מטבע

source_id
target_id
transaction_id
amount
timestamp
currency


how does the account node looks?
account_id


"""

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

class TransactionRepository:
    def __init__(self, driver):
        self.driver = driver

    def create_transaction(self, transaction_data):
        # TODO: create transaction node in neo4j db
        # todo: create a session
        # todo: create a cipher query
        # todo: run with the session, the query
        # todo: return the transaction that was inserted
        pass

    def get_transaction(self, transaction_id):
        #TODO: create a session
        #todo: create a cipher query
        #todo: run with the session, the query
        #todo: return the transaction that was found
        pass

@app.route('/api/v1/transaction', methods=['POST'])
def create_transaction():
    return jsonify({"message": "Transaction created"}), 200


@app.route('/api/v1/transaction/<transaction_id>', methods=['GET'])
def get_transaction():
    return jsonify({"message": "Transaction recieved"}), 200


@app.route('/api/v1/transaction/search', methods=['GET'])
def search_transactions():
    return jsonify({"message": "Transaction searched"}), 200




if __name__ == "__main__":
    print("Running the transaction service flask app")
    app.run(host='0.0.0.0', port=5001, debug=True)
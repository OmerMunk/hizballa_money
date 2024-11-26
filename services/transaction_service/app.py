from flask import Flask, jsonify, request
from neo4j import GraphDatabase
import redis
import uuid
import json



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
        with self.driver.session() as session:
            query = """
            MERGE (source:Account {account_id: $source_id})
            MERGE (target:Account {account_id: $target_id})
            CREATE (source)-[t:TRANSACTION {
                transaction_id: $transaction_id,
                amount: $amount,
                timestamp: datetime($timestamp),
                currency: $currency
            }]->(target)
            RETURN t.id as transaction_id
            """
            result = session.run(query, {
                'source_id': transaction_data['source_id'],
                'target_id': transaction_data['target_id'],
                # the transaction id is generated by the uuid library
                'transaction_id': str(uuid.uuid4()),
                'amount': transaction_data['amount'],
                'timestamp': transaction_data['timestamp'],
                'currency': transaction_data['currency']
            })
            return result.single()['transaction_id']


    def get_transaction(self, transaction_id):
        with self.driver.session() as session:
            query = """
            MATCH (source)-[t:TRANSACTION {transaction_id: $transaction_id}]->(target)
            RETURN source.id as source_id,
                    target.id as target_id,
                    t.amount as amount,
                    t.timestamp as timestamp,
                    t.currency as currency
            """
            result = session.run(query, {'transaction_id': transaction_id})
            record = result.single()
            if record:
                return dict(record)
                # return {
                # 'source_id': record['source_id'],
                # 'target_id': record['target_id'],
                # 'amount': record['amount'],
                # 'timestamp': record['timestamp'],
                # 'currency': record['currency']
                # }
            return None

@app.route('/api/v1/transaction', methods=['POST'])
def create_transaction():
    data = request.get_json()
    required_fields = ['source_id', 'target_id', 'amount', 'timestamp', 'currency']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        repo = TransactionRepository(neo4j_driver)
        transaction_id = repo.create_transaction(data)

        redis_client.lpush(
            'recent_transactions',
            json.dumps({**data, 'transaction_id': transaction_id})
        )
        redis_client.ltrim('recent_transactions', 0, 999)

        return jsonify({
            'status': 'success',
            'transaction_id': transaction_id
        }), 201
    except Exception as e:
        print(f'Error in POST /api/v1/transaction: {str(e)}')
        return jsonify({'error': 'internal server error'}), 500



@app.route('/api/v1/transaction/<transaction_id>', methods=['GET'])
def get_transaction():
    return jsonify({"message": "Transaction recieved"}), 200


@app.route('/api/v1/transaction/search', methods=['GET'])
def search_transactions():
    return jsonify({"message": "Transaction searched"}), 200




if __name__ == "__main__":
    print("Running the transaction service flask app")
    app.run(host='0.0.0.0', port=5001, debug=True)
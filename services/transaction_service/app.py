# services/transaction_service/app.py
from flask import Flask, request, jsonify
from neo4j import GraphDatabase
import redis
import json
from datetime import datetime

app = Flask(__name__)

# Database connections
neo4j_driver = GraphDatabase.driver(
    "bolt://neo4j:7687",
    auth=("neo4j", "password")
)

redis_client = redis.Redis(
    host='redis',
    port=6379,
    decode_responses=True
)


class TransactionRepository:
    def __init__(self, driver):
        self.driver = driver

    def create_transaction(self, transaction_data):
        with self.driver.session() as session:
            # Create transaction node
            query = """
            MERGE (source:Account {id: $source_id})
            MERGE (target:Account {id: $target_id})
            CREATE (source)-[t:TRANSACTION {
                id: $transaction_id,
                amount: $amount,
                timestamp: datetime($timestamp),
                currency: $currency
            }]->(target)
            RETURN t.id as transaction_id
            """
            result = session.run(query, {
                'source_id': transaction_data['source_id'],
                'target_id': transaction_data['target_id'],
                'transaction_id': str(datetime.now().timestamp()),
                'amount': transaction_data['amount'],
                'timestamp': transaction_data['timestamp'],
                'currency': transaction_data['currency']
            })
            return result.single()['transaction_id']

    def get_transaction(self, transaction_id):
        with self.driver.session() as session:
            query = """
            MATCH (source)-[t:TRANSACTION {id: $transaction_id}]->(target)
            RETURN source.id as source_id, 
                   target.id as target_id,
                   t.amount as amount,
                   t.currency as currency,
                   t.timestamp as timestamp
            """
            result = session.run(query, {'transaction_id': transaction_id})
            record = result.single()
            if record:
                return {
                    'source_id': record['source_id'],
                    'target_id': record['target_id'],
                    'amount': record['amount'],
                    'currency': record['currency'],
                    'timestamp': record['timestamp']
                }
            return None


@app.route('/api/v1/transactions', methods=['POST'])
def create_transaction():
    data = request.json
    required_fields = ['source_id', 'target_id', 'amount', 'currency']

    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        data['timestamp'] = datetime.now().isoformat()
        repo = TransactionRepository(neo4j_driver)
        transaction_id = repo.create_transaction(data)

        # Cache recent transaction in Redis
        redis_client.lpush(
            'recent_transactions',
            json.dumps({**data, 'transaction_id': transaction_id})
        )
        redis_client.ltrim('recent_transactions', 0, 999)  # Keep last 1000 transactions

        return jsonify({
            'status': 'success',
            'transaction_id': transaction_id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/transactions/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    try:
        repo = TransactionRepository(neo4j_driver)
        transaction = repo.get_transaction(transaction_id)

        if transaction:
            return jsonify(transaction), 200
        return jsonify({'error': 'Transaction not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/transactions/search', methods=['GET'])
def search_transactions():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    min_amount = request.args.get('min_amount')

    with neo4j_driver.session() as session:
        query = """
        MATCH (source)-[t:TRANSACTION]->(target)
        WHERE 
            ($start_date IS NULL OR t.timestamp >= datetime($start_date)) AND
            ($end_date IS NULL OR t.timestamp <= datetime($end_date)) AND
            ($min_amount IS NULL OR t.amount >= $min_amount)
        RETURN source.id as source_id,
               target.id as target_id,
               t.id as transaction_id,
               t.amount as amount,
               t.currency as currency,
               t.timestamp as timestamp
        ORDER BY t.timestamp DESC
        LIMIT 100
        """

        result = session.run(query, {
            'start_date': start_date,
            'end_date': end_date,
            'min_amount': float(min_amount) if min_amount else None
        })

        transactions = [{
            'transaction_id': record['transaction_id'],
            'source_id': record['source_id'],
            'target_id': record['target_id'],
            'amount': record['amount'],
            'currency': record['currency'],
            'timestamp': record['timestamp']
        } for record in result]

        return jsonify(transactions), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
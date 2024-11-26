from flask import Blueprint, request, jsonify, current_app
import json
import logging


from neo4j_service import TransactionRepository

transaction_bp = Blueprint('transaction_bp', __name__)

@transaction_bp.route('/', methods=['POST'])
def create_transaction():
    data = request.get_json()
    required_fields = ['source_id', 'target_id', 'amount', 'timestamp', 'currency']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        repo = TransactionRepository(current_app.neo4j_driver)
        transaction_id = repo.create_transaction(data)
        current_app.redis_client.lpush(
            'recent_transactions',
            json.dumps({**data, 'transaction_id': transaction_id})
        )
        current_app.redis_client.ltrim('recent_transactions', 0, 999)

        return jsonify({
            'status': 'success',
            'transaction_id': transaction_id
        }), 201
    except Exception as e:
        print(f'Error in POST /api/v1/transaction: {str(e)}')
        logging.error(f'Error in POST /api/v1/transaction: {str(e)}')
        return jsonify({'error': 'internal server error'}), 500

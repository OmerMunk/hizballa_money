from flask import Flask, jsonify, request
import logging

from init_db import init_neo4j, init_redis
from transaction_bp import transaction_bp


app = Flask(__name__)

app.config['DEBUG'] = True
app.config['LOGGING_LEVEL'] = logging.DEBUG



@app.route('/api/v1/transaction/<transaction_id>', methods=['GET'])
def get_transaction():
    return jsonify({"message": "Transaction recieved"}), 200


@app.route('/api/v1/transaction/search', methods=['GET'])
def search_transactions():
    return jsonify({"message": "Transaction searched"}), 200



app.register_blueprint(transaction_bp, url_prefix='/api/v1/transaction')


with app.app_context():
    app.neo4j_driver = init_neo4j()
    app.redis_client = init_redis()

if __name__ == "__main__":
    print("Running the transaction service flask app")
    # init_neo4j()
    # init_redis()
    app.run(host='0.0.0.0', port=5001, debug=True)
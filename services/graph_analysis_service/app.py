import json

import logging

from flask import Flask, request, jsonify, current_app

from analysis_bp import analysis_bp
from init_db import init_neo4j, init_redis

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['LOGGING_LEVEL'] = logging.DEBUG






app.register_blueprint(analysis_bp, url_prefix='/api/v1/analysis')


with app.app_context():
    app.neo4j_driver = init_neo4j()
    app.redis_client = init_redis()

if __name__ == "__main__":
    print("Running the graph analysis service flask app")
    # init_neo4j()
    # init_redis()
    app.run(host='0.0.0.0', port=5002, debug=True)
# services/analysis_service/app.py
from flask import Flask, request, jsonify, send_file
import networkx as nx
from neo4j import GraphDatabase
import redis
import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta
import json

app = Flask(__name__)

neo4j_driver = GraphDatabase.driver(
    "bolt://neo4j:7687",
    auth=("neo4j", "password")
)

redis_client = redis.Redis(
    host='redis',
    port=6379,
    decode_responses=True
)


class GraphAnalyzer:
    def __init__(self, driver):
        self.driver = driver

    def find_circular_patterns(self, min_amount=10000, max_depth=4):
        with self.driver.session() as session:
            query = """
            MATCH path = (a:Account)-[:TRANSACTION*1..%d]->(a)
            WHERE ALL(r IN relationships(path) WHERE r.amount >= $min_amount)
            RETURN nodes(path) as accounts,
                   relationships(path) as transactions,
                   length(path) as cycle_length
            ORDER BY cycle_length
            LIMIT 10
            """ % max_depth

            result = session.run(query, {'min_amount': min_amount})

            patterns = []
            for record in result:
                pattern = {
                    'accounts': [node['id'] for node in record['accounts']],
                    'transactions': [{
                        'amount': tx['amount'],
                        'currency': tx['currency'],
                        'timestamp': tx['timestamp']
                    } for tx in record['transactions']],
                    'cycle_length': record['cycle_length']
                }
                patterns.append(pattern)

            return patterns

    def calculate_metrics(self, timeframe_hours=24):
        with self.driver.session() as session:
            query = """
            MATCH (source)-[t:TRANSACTION]->(target)
            WHERE t.timestamp >= datetime($start_time)
            RETURN count(t) as total_transactions,
                   sum(t.amount) as total_amount,
                   avg(t.amount) as avg_amount,
                   collect(t.amount) as amounts
            """

            start_time = (datetime.now() - timedelta(hours=timeframe_hours)).isoformat()
            result = session.run(query, {'start_time': start_time})
            record = result.single()

            amounts = pd.Series(record['amounts'])
            metrics = {
                'total_transactions': record['total_transactions'],
                'total_amount': record['total_amount'],
                'avg_amount': record['avg_amount'],
                'std_dev': amounts.std(),
                'percentiles': {
                    '25': amounts.quantile(0.25),
                    '50': amounts.quantile(0.50),
                    '75': amounts.quantile(0.75),
                    '90': amounts.quantile(0.90)
                }
            }

            return metrics

    def generate_network_visualization(self, min_amount=50000):
        with self.driver.session() as session:
            query = """
            MATCH (source)-[t:TRANSACTION]->(target)
            WHERE t.amount >= $min_amount
            RETURN source.id as source,
                   target.id as target,
                   t.amount as amount
            LIMIT 100
            """

            result = session.run(query, {'min_amount': min_amount})

            G = nx.DiGraph()
            for record in result:
                G.add_edge(
                    record['source'],
                    record['target'],
                    weight=record['amount']
                )

            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(G)
            nx.draw(
                G, pos,
                with_labels=True,
                node_color='lightblue',
                node_size=500,
                arrowsize=20,
                font_size=8
            )

            # Save plot to bytes buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()

            return buf


@app.route('/api/v1/analysis/patterns', methods=['GET'])
def analyze_patterns():
    min_amount = float(request.args.get('min_amount', 10000))
    max_depth = int(request.args.get('max_depth', 4))

    try:
        analyzer = GraphAnalyzer(neo4j_driver)
        patterns = analyzer.find_circular_patterns(min_amount, max_depth)

        # Cache the results
        cache_key = f'patterns_{min_amount}_{max_depth}'
        redis_client.setex(
            cache_key,
            3600,  # Cache for 1 hour
            json.dumps(patterns)
        )

        return jsonify(patterns), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/analysis/metrics', methods=['GET'])
def get_metrics():
    timeframe = int(request.args.get('timeframe_hours', 24))
    cache_key = f'metrics_{timeframe}'

    # Try to get from cache
    cached_metrics = redis_client.get(cache_key)
    if cached_metrics:
        return jsonify(json.loads(cached_metrics)), 200

    try:
        analyzer = GraphAnalyzer(neo4j_driver)
        metrics = analyzer.calculate_metrics(timeframe)

        # Cache the results
        redis_client.setex(
            cache_key,
            300,  # Cache for 5 minutes
            json.dumps(metrics)
        )

        return jsonify(metrics), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/analysis/visualization', methods=['GET'])
def get_visualization():
    min_amount = float(request.args.get('min_amount', 50000))

    try:
        analyzer = GraphAnalyzer(neo4j_driver)
        buf = analyzer.generate_network_visualization(min_amount)

        return send_file(
            buf,
            mimetype='image/png',
            as_attachment=True,
            download_name='network_visualization.png'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
import json
from datetime import datetime, timedelta
import pandas as pd

from flask import Flask, request, jsonify, current_app

app = Flask(__name__)



"""
GET /api/v1/analysis/patterns
GET /api/v1/analysis/metrics
GET /api/v1/analysis/visualization
"""



class GraphAnalyzer:
    def __init__(self, driver):
        self.driver = driver

    def find_circular_patterns(self, min_amount=10_000):
        with self.driver.session() as session:
            query = """
            MATCH path = (a:Account)-[:TRANSACTION*1..%d]->(a)
            WHERE ALL( r IN relationships(path) WHERE r.amount >= $min_amount)
            RETURN nodes(path) as accounts,
                   relationships(path) as transactions,
                   length(path) as cycle_length
            ORDER BY cycle_length
            LIMIT 10
            """

            result = session.run(query, {'min_amount': min_amount})

            patterns = []
            for record in result:
                """
                לבחון את התוצאות, לראות אם זה נגיש להבין מי העביר מה וכמה
                אם לא - לנסות למצוא פיתרון איך לעצב את מה שחוזר כדי שיהיה לאנליסט נוח
                """
                pattern = {

                    'accounts': [node['id'] for node in record['accounts']],
                    'transactions': [
                        {
                            'amount': tx['amount'],
                            'currency': tx['currency'],
                            'timestamp': tx['timestamp']
                        } for tx in record['transactions']
                    ],
                    'cycle_length': record['cycle_length']
                }
                patterns.append(pattern)

            return patterns

            # analysis

            return True
            pass
        pass


    def calculate_metrics(self, timeframe_hours=24):
        with self.driver.session() as session:
            query = """
            MATCH (source)-[t:TRANSACTION]->(target)
            WHERE t.timestamp >= datetime($start_time)
            RETURN sum(t.amount) as total_amount,
                   count(t) as total_transactions,
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
                    '50': amounts.quantile(0.5),
                    '75': amounts.quantile(0.75),
                    '90': amounts.quantile(0.9),
                }
            }

            return metrics




    def generate_network_visualization(self):
        pass


@app.route('/api/v1/analysis/patterns', methods=['GET'])
def analyze_patterns():
    min_amount = float(request.args.get('min_amount', 10_000))

    try:
        cached_result = redis_client.get(f'patterns_{min_amount}')
        if cached_result:
            return jsonify(json.loads(cached_result)), 200

        analyzer = GraphAnalyzer(app.neo4j_driver)
        patterns = analyzer.find_circular_patterns(min_amount)

        # cache the results
        cache_key = f'patterns_{min_amount}'

        redis_client.setex(
            cache_key,
            3600, # 1 hour,
            json.dumps(patterns)
        )

        return jsonify(patterns), 200

    except:
        pass
    pass


@app.route('/api/v1/analysis/metrics', methods=['GET'])
def get_metrics():
    timeframe = int(request.args.get('timeframe_hours', 24))
    cache_key = f'metrics_{timeframe}'

    # קודם כל בוא ננסה להביא מהקאש
    cached_metrics = current_app.redis_client.get(cache_key)
    if cached_metrics:
        return jsonify(json.loads(cached_metrics)), 200

    try:
        analyzer = GraphAnalyzer(current_app.neo4j_driver)
        metrics = analyzer.calculate_metrics(timeframe)

        current_app.redis_client.setex(
            cache_key,
            600, # 10 minutes
        json.dumps(metrics)
        )

        return jsonify(metrics), 200
    except Exception as ex:
        print(ex)
        return jsonify({"error": str(ex)}), 500


@app.route('/api/v1/analysis/visualization', methods=['GET'])
def get_visualization():
    return "Patterns Analysis"






if __name__ == "__main__":
    app.run(
        debug=True,
        port=5002,
        host='0.0.0.0'
    )
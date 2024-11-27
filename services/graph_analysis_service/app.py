import json

from flask import Flask, request, jsonify


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


    def calculate_metrics(self):
        pass


    def generate_network_visualization(self):
        pass


@app.route('/api/v1/analysis/patterns', methods=['GET'])
def analyze_patterns():
    min_amount = request.args.get('min_amount', 10_000)

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
    return "Patterns Analysis"


@app.route('/api/v1/analysis/visualization', methods=['GET'])
def get_visualization():
    return "Patterns Analysis"






if __name__ == "__main__":
    app.run(
        debug=True,
        port=5002,
        host='0.0.0.0'
    )
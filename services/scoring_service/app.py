# services/scoring_service/app.py
from flask import Flask, request, jsonify
from neo4j import GraphDatabase
import redis
import json
from datetime import datetime, timedelta
import numpy as np

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


class RiskScorer:
    def __init__(self, driver, redis_client):
        self.driver = driver
        self.redis_client = redis_client

    def calculate_entity_risk_score(self, entity_id):
        # Check cache first
        cached_score = self.redis_client.get(f'risk_score:{entity_id}')
        if cached_score:
            return float(cached_score)

        with self.driver.session() as session:
            # Calculate various risk factors
            query = """
            MATCH (a:Account {id: $entity_id})
            OPTIONAL MATCH (a)-[t:TRANSACTION]->(target)
            OPTIONAL MATCH (source)-[t2:TRANSACTION]->(a)
            WITH a,
                 collect(t) as outgoing,
                 collect(t2) as incoming
            RETURN
                size(outgoing) as out_tx_count,
                size(incoming) as in_tx_count,
                reduce(s=0, x IN outgoing | s + x.amount) as total_out,
                reduce(s=0, x IN incoming | s + x.amount) as total_in,
                [x IN outgoing | x.amount] as out_amounts,
                [x IN incoming | x.amount] as in_amounts
            """

            result = session.run(query, {'entity_id': entity_id})
            record = result.single()

            if not record:
                return 0

            # Calculate risk factors
            risk_factors = {
                'transaction_volume': self._calculate_volume_risk(
                    record['out_tx_count'],
                    record['in_tx_count']
                ),
                'amount_variance': self._calculate_amount_variance_risk(
                    record['out_amounts'],
                    record['in_amounts']
                ),
                'balance_ratio': self._calculate_balance_ratio_risk(
                    record['total_out'],
                    record['total_in']
                ),
                'pattern_risk': self._calculate_pattern_risk(entity_id, session)
            }

            # Calculate final score (0-100)
            final_score = sum(risk_factors.values()) / len(risk_factors)

            # services/scoring_service/app.py (continued)
            # Cache the score
            self.redis_client.setex(
                f'risk_score:{entity_id}',
                3600,  # Cache for 1 hour
                str(final_score)
            )

            return final_score

        def _calculate_volume_risk(self, out_count, in_count):
            total_count = out_count + in_count
            if total_count == 0:
                return 0

            # Higher transaction counts indicate higher risk
            if total_count > 1000:
                return 100
            return (total_count / 1000) * 100

        def _calculate_amount_variance_risk(self, out_amounts, in_amounts):
            if not out_amounts and not in_amounts:
                return 0

            all_amounts = out_amounts + in_amounts
            if len(all_amounts) < 2:
                return 0

            std_dev = np.std(all_amounts)
            mean = np.mean(all_amounts)

            # High variance relative to mean indicates higher risk
            cv = (std_dev / mean) if mean > 0 else 0
            return min(100, cv * 50)  # Scale coefficient of variation to 0-100

        def _calculate_balance_ratio_risk(self, total_out, total_in):
            if total_in == 0 or total_out == 0:
                return 0

            ratio = total_out / total_in

            # Ratios close to 1 might indicate money laundering
            if 0.95 <= ratio <= 1.05:
                return 100
            elif 0.90 <= ratio <= 1.10:
                return 75
            elif 0.80 <= ratio <= 1.20:
                return 50
            return 25

        def _calculate_pattern_risk(self, entity_id, session):
            # Check for circular patterns
            query = """
                    MATCH path = (a:Account {id: $entity_id})-[:TRANSACTION*1..4]->(a)
                    RETURN count(path) as cycle_count
                    """

            result = session.run(query, {'entity_id': entity_id})
            cycle_count = result.single()['cycle_count']

            # Any circular patterns are highly suspicious
            return min(100, cycle_count * 25)

        @app.route('/api/v1/risk-score/<entity_id>', methods=['GET'])
        def get_risk_score(entity_id):
            try:
                scorer = RiskScorer(neo4j_driver, redis_client)
                score = scorer.calculate_entity_risk_score(entity_id)

                return jsonify({
                    'entity_id': entity_id,
                    'risk_score': score,
                    'risk_level': 'HIGH' if score >= 75 else 'MEDIUM' if score >= 50 else 'LOW',
                    'timestamp': datetime.now().isoformat()
                }), 200

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/v1/blacklist', methods=['POST'])
        def add_to_blacklist():
            data = request.json
            if 'entity_id' not in data:
                return jsonify({'error': 'Missing entity_id'}), 400

            try:
                # Add to Redis set
                redis_client.sadd('blacklisted_entities', data['entity_id'])

                # Store additional information
                redis_client.hset(
                    f'blacklist_info:{data["entity_id"]}',
                    mapping={
                        'timestamp': datetime.now().isoformat(),
                        'reason': data.get('reason', 'Not specified'),
                        'risk_score': data.get('risk_score', 'N/A')
                    }
                )

                return jsonify({
                    'status': 'success',
                    'message': f'Entity {data["entity_id"]} added to blacklist'
                }), 201

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/v1/risk-metrics', methods=['GET'])
        def get_risk_metrics():
            try:
                # Get all risk scores from cache
                all_scores = []
                for key in redis_client.scan_iter("risk_score:*"):
                    score = float(redis_client.get(key))
                    all_scores.append(score)

                if not all_scores:
                    return jsonify({
                        'error': 'No risk scores available'
                    }), 404

                metrics = {
                    'total_entities_scored': len(all_scores),
                    'avg_risk_score': np.mean(all_scores),
                    'high_risk_count': sum(1 for score in all_scores if score >= 75),
                    'medium_risk_count': sum(1 for score in all_scores if 50 <= score < 75),
                    'low_risk_count': sum(1 for score in all_scores if score < 50),
                    'risk_score_distribution': {
                        'min': min(all_scores),
                        'max': max(all_scores),
                        'percentiles': {
                            '25': np.percentile(all_scores, 25),
                            '50': np.percentile(all_scores, 50),
                            '75': np.percentile(all_scores, 75),
                            '90': np.percentile(all_scores, 90)
                        }
                    }
                }

                return jsonify(metrics), 200

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        if __name__ == '__main__':
            app.run(debug=True,host='0.0.0.0', port=5003)
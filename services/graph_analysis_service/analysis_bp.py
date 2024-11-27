from flask import Blueprint, request, jsonify, current_app
import json
import logging



from neo4j_service import GraphAnalyzer

analysis_bp = Blueprint('transaction_bp', __name__)

@analysis_bp.route('/patterns', methods=['GET'])
def analyze_patterns():
    min_amount = float(request.args.get('min_amount', 10_000))

    try:
        cached_result = current_app.redis_client.get(f'patterns_{min_amount}')
        if cached_result:
            return jsonify(json.loads(cached_result)), 200

        analyzer = GraphAnalyzer(current_app.neo4j_driver)
        patterns = analyzer.find_circular_patterns(min_amount)

        # cache the results
        cache_key = f'patterns_{min_amount}'

        current_app.redis_client.setex(
            cache_key,
            3600, # 1 hour,
            json.dumps(patterns)
        )

        return jsonify(patterns), 200

    except:
        current_app.logger.error("An error occurred", exc_info=True)
        return jsonify({"error": "An error occurred"}), 500
    pass


@analysis_bp.route('/metrics', methods=['GET'])
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

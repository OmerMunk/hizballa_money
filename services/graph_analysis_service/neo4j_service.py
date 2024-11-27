from datetime import datetime, timedelta
import pandas as pd

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
            """ % 4

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
                            'timestamp': f"{tx['timestamp']}"
                        } for tx in record['transactions']
                    ],
                    'cycle_length': record['cycle_length']
                }
                patterns.append(pattern)

            return patterns


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

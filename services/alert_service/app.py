import requests
import json
import time
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
import smtplib
from email.message import EmailMessage
import os


class FinancialMonitor:
    def __init__(self):
        self.setup_logging()
        self.base_url = "http://localhost:5001"
        self.analysis_url = "http://localhost:5002"
        self.scoring_url = "http://localhost:5003"

        # Alert thresholds
        self.thresholds = {
            'high_risk_ratio': 0.1,  # 10% high risk transactions
            'circular_pattern_count': 3,  # Number of circular patterns
            'large_transaction_amount': 1000000,  # $1M
            'rapid_transaction_count': 100  # Transactions per hour
        }

    def setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger('FinancialMonitor')
        self.logger.setLevel(logging.INFO)

        # Create handlers
        file_handler = RotatingFileHandler(
            'financial_monitor.log',
            maxBytes=1024 * 1024,  # 1MB
            backupCount=5
        )
        console_handler = logging.StreamHandler()

        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def send_alert(self, subject, message):
        """Send alert email"""
        self.logger.warning(f"ALERT: {subject}")
        self.logger.warning(message)

        # In production, you would configure email sending here
        # For the exercise, we'll just log the alerts

    def check_high_risk_ratio(self):
        """Monitor ratio of high-risk transactions"""
        try:
            response = requests.get(f"{self.scoring_url}/api/v1/risk-metrics")
            metrics = response.json()

            total_entities = metrics['total_entities_scored']
            high_risk = metrics['high_risk_count']

            if total_entities > 0:
                ratio = high_risk / total_entities
                if ratio > self.thresholds['high_risk_ratio']:
                    self.send_alert(
                        "High Risk Transaction Ratio Alert",
                        f"High risk transactions ratio ({ratio:.2%}) exceeds threshold"
                    )

        except Exception as e:
            self.logger.error(f"Error checking risk ratio: {str(e)}")

    def check_circular_patterns(self):
        """Monitor for circular transaction patterns"""
        try:
            response = requests.get(
                f"{self.analysis_url}/api/v1/analysis/patterns",
                params={"min_amount": 50000}
            )
            patterns = response.json()

            if len(patterns) >= self.thresholds['circular_pattern_count']:
                self.send_alert(
                    "Circular Pattern Alert",
                    f"Detected {len(patterns)} circular patterns"
                )

                # Log details of each pattern
                for pattern in patterns:
                    self.logger.info(f"Circular Pattern: {json.dumps(pattern)}")

        except Exception as e:
            self.logger.error(f"Error checking circular patterns: {str(e)}")

    def check_large_transactions(self):
        """Monitor for unusually large transactions"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/transactions/search",
                params={"min_amount": self.thresholds['large_transaction_amount']}
            )
            transactions = response.json()

            if transactions:
                self.send_alert(
                    "Large Transaction Alert",
                    f"Detected {len(transactions)} transactions over "
                    f"${self.thresholds['large_transaction_amount']:,}"
                )

                for tx in transactions:
                    self.logger.info(f"Large Transaction: {json.dumps(tx)}")

        except Exception as e:
            self.logger.error(f"Error checking large transactions: {str(e)}")

    def check_transaction_velocity(self):
        """Monitor transaction velocity (rate)"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)

            response = requests.get(
                f"{self.base_url}/api/v1/transactions/search",
                params={
                    "start_date": start_time.isoformat(),
                    "end_date": end_time.isoformat()
                }
            )
            transactions = response.json()

            if len(transactions) > self.thresholds['rapid_transaction_count']:
                self.send_alert(
                    "High Transaction Velocity Alert",
                    f"Detected {len(transactions)} transactions in the last hour"
                )

        except Exception as e:
            self.logger.error(f"Error checking transaction velocity: {str(e)}")

    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle"""
        self.logger.info("Starting monitoring cycle...")

        self.check_high_risk_ratio()
        self.check_circular_patterns()
        self.check_large_transactions()
        self.check_transaction_velocity()

        self.logger.info("Monitoring cycle completed")

    def start_monitoring(self, interval_seconds=300):
        """Start continuous monitoring"""
        self.logger.info("Starting Financial Intelligence Monitoring System")

        while True:
            try:
                self.run_monitoring_cycle()
                time.sleep(interval_seconds)

            except KeyboardInterrupt:
                self.logger.info("Monitoring stopped by user")
                break

            except Exception as e:
                self.logger.error(f"Error in monitoring cycle: {str(e)}")
                time.sleep(60)  # Wait before retrying


if __name__ == "__main__":
    monitor = FinancialMonitor()
    monitor.start_monitoring()
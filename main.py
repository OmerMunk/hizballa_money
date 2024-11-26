"""
This script demonstrates common usage scenarios for the Financial Intelligence System.
Run each scenario separately to understand the system's capabilities.
"""

import requests
import json
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd

# Configuration
BASE_URL = "http://localhost:5001"
ANALYSIS_URL = "http://localhost:5002"
SCORING_URL = "http://localhost:5003"


def scenario_1_basic_transaction():
    """
    תרחיש 1: יצירת העברה בסיסית וקבלת המידע עליה
    """
    print("=== תרחיש 1: העברה בסיסית ===")

    # Create transaction
    transaction_data = {
        "source_id": "ACC_0001",
        "target_id": "ACC_0002",
        "amount": 50000,
        "currency": "USD"
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/transactions",
        json=transaction_data
    )

    transaction_id = response.json()['transaction_id']
    print(f"נוצרה העברה חדשה: {transaction_id}")

    # Get transaction details
    response = requests.get(
        f"{BASE_URL}/api/v1/transactions/{transaction_id}"
    )
    print("פרטי ההעברה:", json.dumps(response.json(), indent=2))


def scenario_2_circular_pattern():
    """
    תרחיש 2: יצירת דפוס העברות מעגלי
    """
    print("\n=== תרחיש 2: דפוס העברות מעגלי ===")

    # Create circular pattern
    accounts = ["ACC_0003", "ACC_0004", "ACC_0005"]
    amount = 75000

    for i in range(len(accounts)):
        transaction_data = {
            "source_id": accounts[i],
            "target_id": accounts[(i + 1) % len(accounts)],
            "amount": amount,
            "currency": "USD"
        }

        requests.post(
            f"{BASE_URL}/api/v1/transactions",
            json=transaction_data
        )
        time.sleep(1)  # Add delay between transactions

    # Analyze patterns
    response = requests.get(
        f"{ANALYSIS_URL}/api/v1/analysis/patterns",
        params={"min_amount": amount - 1000}
    )

    patterns = response.json()
    print(f"זוהו {len(patterns)} דפוסים מעגליים")
    for pattern in patterns:
        print("דפוס:", json.dumps(pattern, indent=2))


def scenario_3_risk_analysis():
    """
    תרחיש 3: ניתוח סיכונים
    """
    print("\n=== תרחיש 3: ניתוח סיכונים ===")

    # Get risk score for entity
    entity_id = "ACC_0003"
    response = requests.get(
        f"{SCORING_URL}/api/v1/risk-score/{entity_id}"
    )

    risk_data = response.json()
    print(f"ציון סיכון עבור {entity_id}:", json.dumps(risk_data, indent=2))

    # Add to blacklist if high risk
    if risk_data['risk_score'] >= 75:
        blacklist_data = {
            "entity_id": entity_id,
            "reason": "High risk score from circular pattern",
            "risk_score": risk_data['risk_score']
        }

        requests.post(
            f"{SCORING_URL}/api/v1/blacklist",
            json=blacklist_data
        )
        print(f"החשבון {entity_id} נוסף לרשימה השחורה")


def scenario_4_time_analysis():
    """
    תרחיש 4: ניתוח מגמות לאורך זמן
    """
    print("\n=== תרחיש 4: ניתוח מגמות ===")

    # Get transactions for last 24 hours
    end_date = datetime.now().isoformat()
    start_date = (datetime.now() - timedelta(hours=24)).isoformat()

    response = requests.get(
        f"{BASE_URL}/api/v1/transactions/search",
        params={
            "start_date": start_date,
            "end_date": end_date
        }
    )

    transactions = response.json()
    df = pd.DataFrame(transactions)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Analyze hourly patterns
    hourly_volume = df.resample('H', on='timestamp')['amount'].sum()

    plt.figure(figsize=(12, 6))
    hourly_volume.plot(title='Transaction Volume by Hour')
    plt.xlabel('Hour')
    plt.ylabel('Total Amount')
    plt.show()


def scenario_5_network_visualization():
    """
    תרחיש 5: ויזואליזציה של רשת העברות
    """
    print("\n=== תרחיש 5: ויזואליזציה של רשת ===")

    response = requests.get(
        f"{ANALYSIS_URL}/api/v1/analysis/visualization",
        params={"min_amount": 50000}
    )

    if response.status_code == 200:
        # Save visualization
        with open('network.png', 'wb') as f:
            f.write(response.content)
        print("הויזואליזציה נשמרה בקובץ network.png")


if __name__ == "__main__":
    print("מתחיל הדגמת תרחישים...")

    try:
        scenario_1_basic_transaction()
        scenario_2_circular_pattern()
        scenario_3_risk_analysis()
        scenario_4_time_analysis()
        scenario_5_network_visualization()

    except Exception as e:
        print(f"שגיאה בהרצת התרחישים: {str(e)}")
import random
from datetime import datetime, timedelta
import requests
import json
import time


class SuspiciousPatternGenerator:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.account_ids = [f"ACC_{i:04d}" for i in range(100)]
        self.currencies = ["USD", "EUR", "GBP"]

    def generate_normal_transaction(self):
        """Generate a legitimate-looking transaction"""
        source = random.choice(self.account_ids)
        target = random.choice([acc for acc in self.account_ids if acc != source])

        return {
            "source_id": source,
            "target_id": target,
            "amount": round(random.uniform(1000, 50000), 2),
            "currency": random.choice(self.currencies)
        }

    def generate_circular_pattern(self, num_accounts=3):
        """Generate a suspicious circular pattern"""
        accounts = random.sample(self.account_ids, num_accounts)
        base_amount = random.uniform(75000, 150000)

        transactions = []
        for i in range(num_accounts):
            amount = base_amount * random.uniform(0.95, 1.05)  # Slight variation

            transactions.append({
                "source_id": accounts[i],
                "target_id": accounts[(i + 1) % num_accounts],
                "amount": round(amount, 2),
                "currency": random.choice(self.currencies)
            })

        return transactions

    def generate_layering_pattern(self):
        """Generate a layering pattern to obscure source"""
        main_amount = random.uniform(200000, 500000)
        num_layers = random.randint(3, 5)

        transactions = []
        current_accounts = [random.choice(self.account_ids)]

        for layer in range(num_layers):
            next_accounts = random.sample(
                [acc for acc in self.account_ids if acc not in current_accounts],
                len(current_accounts) * 2
            )

            amount_per_tx = main_amount / len(next_accounts)

            for source in current_accounts:
                for _ in range(2):  # Split into two
                    target = next_accounts.pop()
                    transactions.append({
                        "source_id": source,
                        "target_id": target,
                        "amount": round(amount_per_tx * random.uniform(0.9, 1.1), 2),
                        "currency": random.choice(self.currencies)
                    })

            current_accounts = next_accounts
            main_amount = amount_per_tx

        return transactions

    def generate_structuring_pattern(self):
        """Generate a structuring pattern (multiple small transactions)"""
        source = random.choice(self.account_ids)
        target = random.choice([acc for acc in self.account_ids if acc != source])
        total_amount = random.uniform(100000, 200000)

        transactions = []
        remaining_amount = total_amount

        while remaining_amount > 0:
            amount = min(9000, remaining_amount * random.uniform(0.1, 0.3))
            remaining_amount -= amount

            transactions.append({
                "source_id": source,
                "target_id": target,
                "amount": round(amount, 2),
                "currency": random.choice(self.currencies)
            })

        return transactions

    def generate_dataset(self):
        """Generate a complete dataset with various patterns"""
        all_transactions = []

        # Add normal transactions
        for _ in range(1000):
            all_transactions.append(self.generate_normal_transaction())

        # Add circular patterns
        for _ in range(3):
            all_transactions.extend(
                self.generate_circular_pattern(
                    num_accounts=random.randint(3, 5)
                )
            )

        # Add layering patterns
        for _ in range(2):
            all_transactions.extend(self.generate_layering_pattern())

        # Add structuring patterns
        for _ in range(5):
            all_transactions.extend(self.generate_structuring_pattern())

        # Sort by timestamp
        all_transactions.sort(
            key=lambda x: datetime.now() - timedelta(
                minutes=random.randint(0, 24 * 60)
            )
        )

        return all_transactions

    def send_transactions(self, transactions, delay=0.1):
        """Send transactions to the API"""
        results = []
        for tx in transactions:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/transactions",
                    json=tx
                )
                results.append({
                    'transaction': tx,
                    'status': response.status_code,
                    'response': response.json()
                })
                time.sleep(delay)  # Add delay between transactions

            except Exception as e:
                results.append({
                    'transaction': tx,
                    'status': 'error',
                    'error': str(e)
                })

            return results

    def generate_and_send(self, output_file='generated_data.json'):
        """Generate and send data, saving results"""
        print("Generating suspicious financial patterns...")
        transactions = self.generate_dataset()

        print(f"Generated {len(transactions)} transactions")
        print("Sending to API...")

        results = self.send_transactions(transactions)

        # Save results
        with open(output_file, 'w') as f:
            json.dump({
                'transactions': transactions,
                'results': results
            }, f, indent=2)

        print(f"Results saved to {output_file}")

        # Print summary
        success = sum(1 for r in results if isinstance(r['status'], int) and r['status'] == 201)
        print(f"\nSummary:")
        print(f"Total Transactions: {len(transactions)}")
        print(f"Successfully Sent: {success}")
        print(f"Failed: {len(transactions) - success}")

def main():
    """Main function to run the generator"""
    generator = SuspiciousPatternGenerator()

    print("=== Financial Intelligence System Test Data Generator ===")
    print("\nThis script will generate test data including:")
    print("1. Normal transactions")
    print("2. Circular money laundering patterns")
    print("3. Layering patterns")
    print("4. Structuring patterns (smurfing)")

    try:
        generator.generate_and_send()
        print("\nData generation completed successfully!")

    except Exception as e:
        print(f"\nError during data generation: {str(e)}")

    print("\nYou can now:")
    print("1. Use the Analysis Service to detect patterns")
    print("2. Check Risk Scores for involved accounts")
    print("3. Visualize the transaction network")
    print("4. Review the generated data in generated_data.json")

if __name__ == "__main__":
    main()

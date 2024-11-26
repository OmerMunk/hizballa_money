def calculate_transaction_metrics(transactions):
    """Calculate basic metrics for a set of transactions."""
    if not transactions:
        return {}

    amounts = [tx['amount'] for tx in transactions]
    return {
        'count': len(transactions),
        'total_amount': sum(amounts),
        'average_amount': sum(amounts) / len(amounts),
        'max_amount': max(amounts),
        'min_amount': min(amounts)
    }
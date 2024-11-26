
from datetime import datetime
import re


def validate_account_id(account_id):
    """Validate account ID format."""
    pattern = r'^ACC_\d{4}$'
    return bool(re.match(pattern, account_id))


def validate_transaction(transaction_data):
    """Validate transaction data."""
    required_fields = {'source_id', 'target_id', 'amount', 'currency'}

    # Check required fields
    if not all(field in transaction_data for field in required_fields):
        return False, "Missing required fields"

    # Validate account IDs
    if not validate_account_id(transaction_data['source_id']):
        return False, "Invalid source account ID format"
    if not validate_account_id(transaction_data['target_id']):
        return False, "Invalid target account ID format"

    # Validate amount
    if not isinstance(transaction_data['amount'], (int, float)):
        return False, "Amount must be a number"
    if transaction_data['amount'] <= 0:
        return False, "Amount must be positive"

    # Validate currency
    valid_currencies = {'USD', 'EUR', 'GBP'}
    if transaction_data['currency'] not in valid_currencies:
        return False, "Invalid currency"

    return True, None

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch
from services.transaction_service.app import app, TransactionRepository


class TestAnalysisService:
    def test_find_patterns_success(self, client, mock_neo4j, mock_redis):
        # Arrange
        mock_session = Mock()
        mock_neo4j.session.return_value.__enter__.return_value = mock_session
        mock_session.run.return_value = [
            {
                "accounts": ["ACC_001", "ACC_002", "ACC_003"],
                "transactions": [
                    {"amount": 50000, "currency": "USD", "timestamp": datetime.now()}
                ],
                "cycle_length": 3
            }
        ]

        # Act
        response = client.get('/api/v1/analysis/patterns?min_amount=10000')

        # Assert
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) > 0

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch
from services.transaction_service.app import app, TransactionRepository


class TestScoringService:
    def test_calculate_risk_score(self, client, mock_neo4j, mock_redis):
        # Arrange
        entity_id = "ACC_0001"
        mock_redis.get.return_value = None  # No cached score

        mock_session = Mock()
        mock_neo4j.session.return_value.__enter__.return_value = mock_session
        mock_session.run.return_value.single.return_value = {
            "out_tx_count": 10,
            "in_tx_count": 8,
            "total_out": 100000,
            "total_in": 95000,
            "out_amounts": [10000] * 10,
            "in_amounts": [11875] * 8
        }

        # Act
        response = client.get(f'/api/v1/risk-score/{entity_id}')

        # Assert
        assert response.status_code == 200
        assert 'risk_score' in response.json
        assert 'risk_level' in response.json

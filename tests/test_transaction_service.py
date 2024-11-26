import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch
from services.transaction_service.app import app, TransactionRepository


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_neo4j():
    with patch('neo4j.GraphDatabase') as mock:
        yield mock


@pytest.fixture
def mock_redis():
    with patch('redis.Redis') as mock:
        yield mock


class TestTransactionService:
    def test_create_transaction_success(self, client, mock_neo4j, mock_redis):
        # Arrange
        test_data = {
            "source_id": "ACC_0001",
            "target_id": "ACC_0002",
            "amount": 50000,
            "currency": "USD"
        }

        mock_session = Mock()
        mock_neo4j.session.return_value.__enter__.return_value = mock_session
        mock_session.run.return_value.single.return_value = {"transaction_id": "123"}

        # Act
        response = client.post(
            '/api/v1/transactions',
            json=test_data
        )

        # Assert
        assert response.status_code == 201
        assert 'transaction_id' in response.json

    def test_create_transaction_missing_fields(self, client):
        # Arrange
        test_data = {
            "source_id": "ACC_0001",
            # Missing required fields
            "amount": 50000
        }

        # Act
        response = client.post(
            '/api/v1/transactions',
            json=test_data
        )

        # Assert
        assert response.status_code == 400
        assert 'error' in response.json

    def test_get_transaction_success(self, client, mock_neo4j):
        # Arrange
        mock_session = Mock()
        mock_neo4j.session.return_value.__enter__.return_value = mock_session
        mock_session.run.return_value.single.return_value = {
            "source_id": "ACC_0001",
            "target_id": "ACC_0002",
            "amount": 50000,
            "currency": "USD",
            "timestamp": datetime.now()
        }

        # Act
        response = client.get('/api/v1/transactions/123')

        # Assert
        assert response.status_code == 200
        assert 'source_id' in response.json
        assert 'target_id' in response.json





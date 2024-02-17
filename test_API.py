import pytest
from API import get_price_and_percent24h


@pytest.fixture
def mock_requests_get(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = [
        {'symbol': 'BTCUSDT', 'price': '50000', 'priceChangePercent': '1.23'},
        {'symbol': 'ETHUSDT', 'price': '2000', 'priceChangePercent': '2.34'},
    ]
    return mocker.patch('requests.get', return_value=mock_response)


def test_get_price_and_percent24h(mock_requests_get):
    list_symbol = ['BTCUSDT', 'ETHUSDT']
    expected_result = {
        'BTCUSDT': {'price': 50000.0, 'price_change_percent': 1.23},
        'ETHUSDT': {'price': 2000.0, 'price_change_percent': 2.34},
    }
    assert get_price_and_percent24h(list_symbol) == expected_result

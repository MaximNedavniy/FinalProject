import pytest
from database_ import Database


@pytest.fixture
def mock_psycopg2_connect(mocker):
    return mocker.patch('psycopg2.connect')  # Підміна з'єднання з БД


def test_add_coin_to_db(mock_psycopg2_connect):
    with Database(dbname='test_db', user='test_user', password='test_password', host='localhost', port='5432') as db:  # Створення об'єкта БД
        mock_cursor = db.cur  # Мок курсора
        mock_cursor.execute.return_value = None  # Не виконувати реальний sql запит

        db.add_coin_to_db('BTC', count=1, price=50000)
        mock_cursor.execute.assert_called_once_with(
            'INSERT INTO crypto (name_crypto, count, purchase_price) VALUES (%s, %s, %s)',
            # перевіряємо, що execute викликаний з певними параметрами.
            ('BTC', 1.0, 50000.0)
        )

        # перевіряємо, що була викликана команда commit
        db.conn.commit.assert_called_once()


def test_delete_coin(mock_psycopg2_connect):
    with Database(dbname='test_db', user='test_user', password='test_password', host='localhost', port='5432') as db:
        mock_cursor = db.cur
        mock_cursor.execute.return_value = None

        db.delete_coin('BTC')

        mock_cursor.execute.assert_called_once_with(
            'DELETE FROM crypto WHERE name_crypto=%s', ('BTC',))

        db.conn.commit.assert_called_once()


def test_get_list_db(mock_psycopg2_connect):
    with Database(dbname='test_db', user='test_user', password='test_password', host='localhost', port='5432') as db:

        mock_cursor = db.cur
        mock_cursor.fetchall.return_value = [('BTC',), ('ETH',)]

        result = db.get_list_db()

        assert result == ['BTC', 'ETH']


def test_get_count_purchase_price(mock_psycopg2_connect):
    with Database(dbname='test_db', user='test_user', password='test_password', host='localhost', port='5432') as db:
        mock_cursor = db.cur
        mock_cursor.fetchall.return_value = [(1, 50000)]

        result = db.get_count_purchase_price('BTC')

        assert result == [(1, 50000)]

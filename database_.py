import psycopg2


class Database:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def __enter__(self):
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        self.cur = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cur.close()
        self.conn.close()

    def add_coin_to_db(self, name, count=0, price=0):
        try:
            self.cur.execute(
                'INSERT INTO crypto (name_crypto, count, purchase_price) VALUES (%s, %s, %s)',
                (name,
                 float(count),
                    float(price)))
            self.conn.commit()
        except Exception as e:
            print(f"Error add coin_to_db: {e}")

    def delete_coin(self, name):
        try:
            self.cur.execute(
                'DELETE FROM crypto WHERE name_crypto=%s', (name,))
            self.conn.commit()
        except Exception as e:
            print(f"Error deleting record: {e}")

    def get_list_db(self):
        try:
            self.cur.execute(
                'SELECT name_crypto FROM crypto GROUP BY name_crypto')
            data = self.cur.fetchall()
            db_list = list(item[0] for item in data)
            return db_list
        except Exception as e:
            print(f"Error get_count_purchase_price {e}")

    def get_count_purchase_price(self, name):
        try:
            self.cur.execute(
                'SELECT count, purchase_price FROM crypto WHERE name_crypto=%s', (name,))
            data = self.cur.fetchall()
            flat_list = list(item for item in data)
            return flat_list
        except Exception as e:
            print(f"Error get_count_purchase_price {e}")

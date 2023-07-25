from flask_app.config.mysqlconnection import connectToMySQL
from flask import session
from flask_app.models.model_user import User

class Seatingtables:
    db = "wedding_schema"

    def __init__(self, data):
        self.id = data['id']
        self.table = data['table']
        self.seat = data['seat']
        self.guest = data['guest']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']

    @classmethod
    def create(cls, data):
        user_id = session.get('user_id')
        data['user_id'] = user_id
        existing_seat = cls.get_one_user_seat(user_id)
        if existing_seat:
            return None  # Return None or handle the duplicate seat case as per your application logic
        query = """
        INSERT INTO seating_tables (`table`, seat, guest, created_at, updated_at, user_id)
        VALUES (%(table)s, %(seat)s, %(guest)s, NOW(), NOW(), %(user_id)s);
        """
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def get_one(cls, data):
        query = "SELECT * FROM seating_tables WHERE id = %(id)s;"
        result = connectToMySQL(cls.db).query_db(query, data)
        if result:
            return cls(result[0])
        return None

    @classmethod
    def get_one_user_table(cls, user_id):
        query = "SELECT `table` FROM seating_tables WHERE user_id = %(user_id)s LIMIT 1;"
        data = {'user_id': user_id}
        result = connectToMySQL(cls.db).query_db(query, data)
        if result:
            return result[0]['table']
        return None

    @classmethod
    def get_one_user_seat(cls, user_id):
        query = "SELECT seat FROM seating_tables WHERE user_id = %(user_id)s AND guest = 0 LIMIT 1;"
        data = {'user_id': user_id}
        result = connectToMySQL(cls.db).query_db(query, data)
        if result:
            return result[0]['seat']
        return None

    @classmethod
    def get_plus_one_seat(cls, user_id):
        query = "SELECT seat FROM seating_tables WHERE user_id = %(user_id)s AND guest = 1 LIMIT 1;"
        data = {'user_id': user_id}
        result = connectToMySQL(cls.db).query_db(query, data)
        if result:
            return result[0]['seat']
        return None

    @classmethod
    def get_all_tables_with_users(cls):
        query = """
        SELECT seating_tables.*, users.id as user_id, users.first_name, users.last_name, users.email,
        users.password, users.street, users.city, users.zip_code, users.state, users.created_at, users.updated_at
        FROM seating_tables
        LEFT JOIN users ON seating_tables.user_id = users.id;
        """
        results = connectToMySQL(cls.db).query_db(query)
        tables = []
        for result in results:
            table = cls(result)
            if result['user_id']:
                user_data = {
                    'id': result['user_id'],
                    'first_name': result['first_name'],
                    'last_name': result['last_name'],
                    'email': result['email'],
                    'password': result['password'],
                    'street': result['street'],
                    'city': result['city'],
                    'zip_code': result['zip_code'],
                    'state': result['state'],
                    'created_at': result['created_at'],
                    'updated_at': result['updated_at'],
                }
                user = User(user_data)
                table.user = user
            tables.append(table)
        return tables
    
    @classmethod
    def add_plus_one(cls, user_id, guest_seat):
        query = """
        UPDATE seating_tables
        SET guest = 1, seat = %(guest_seat)s, updated_at = NOW()
        WHERE user_id = %(user_id)s;
        """
        data = {
            'user_id': user_id,
            'guest_seat': guest_seat
        }
        connectToMySQL(cls.db).query_db(query, data)

    # @classmethod
    # def update(cls, data):
    #     query = """
    #     UPDATE seating_tables
    #     SET seat = %(seat)s, updated_at = NOW()
    #     WHERE user_id = %(user_id)s;
    #     """
    #     connectToMySQL(cls.db).query_db(query, data)

    # @classmethod
    # def delete_seat(cls, user_id):
    #     query = """
    #     DELETE FROM seating_tables
    #     WHERE user_id = %(user_id)s;
    #     """
    #     data = {
    #         'user_id': user_id
    #     }
    #     connectToMySQL(cls.db).query_db(query, data)

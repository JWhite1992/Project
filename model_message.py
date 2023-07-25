from flask_app.config.mysqlconnection import connectToMySQL
from flask import session
from flask_app.models.model_user import User

class Message:
    db = "wedding_schema"

    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.message = data['message']
        self.like_count = data.get('like_count', 0)
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']
        self.user = None

    @classmethod
    def create(cls, data):
        user_id = session.get('user_id')
        data['user_id'] = user_id
        query = """
        INSERT INTO message_board (name, message, created_at, updated_at, user_id)
        VALUES (%(name)s, %(message)s, NOW(), NOW(), %(user_id)s);
        """
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def update(cls, data):
        query = "UPDATE message_board SET name = %(name)s, message = %(message)s, updated_at = NOW() WHERE id = %(id)s;"
        connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def get_one(cls, message_id):
        query = "SELECT * FROM message_board WHERE id = %(message_id)s;"
        data = {'message_id': message_id}
        result = connectToMySQL(cls.db).query_db(query, data)
        if result:
            return cls(result[0])
        return None

    @classmethod
    def get_one_message_with_user(cls, message_id):
        query = """
        SELECT message_board.*, users.first_name, users.last_name, users.email, users.street, users.city,
        users.zip_code, users.state, users.created_at AS user_created_at, users.updated_at AS user_updated_at,
        users.password
        FROM message_board
        LEFT JOIN users ON message_board.user_id = users.id
        WHERE message_board.id = %(message_id)s;
        """
        data = {'message_id': message_id}
        results = connectToMySQL(cls.db).query_db(query, data)
        if results:
            message_data = results[0]
            user_data = {
                'id': message_data['user_id'],
                'first_name': message_data['first_name'],
                'last_name': message_data['last_name'],
                'email': message_data['email'],
                'street': message_data['street'],
                'city': message_data['city'],
                'zip_code': message_data['zip_code'],
                'state': message_data['state'],
                'created_at': message_data['user_created_at'],
                'updated_at': message_data['user_updated_at'],
                'password': message_data['password'],
            }
            user = User(user_data)
            message = cls(message_data)
            message.user = user
            return message
        return None

    @classmethod
    def get_all_messages(cls):
        query = "SELECT * FROM message_board;"
        results = connectToMySQL(cls.db).query_db(query)
        messages = []
        for result in results:
            messages.append(cls(result))
        return messages

    @classmethod
    def get_all_messages_with_user(cls):
        query = """
        SELECT message_board.*, users.*
        FROM message_board
        LEFT JOIN users ON message_board.user_id = users.id;
        """
        results = connectToMySQL(cls.db).query_db(query)
        messages = []
        for result in results:
            message = cls(result)
            if result['user_id']:
                user_data = {
                    'id': result['user_id'],
                    'first_name': result['first_name'],
                    'last_name': result['last_name'],
                    'email': result['email'],
                    'street': result['street'],
                    'city': result['city'],
                    'zip_code': result['zip_code'],
                    'state': result['state'],
                    'created_at': result['created_at'],
                    'updated_at': result['updated_at'],
                }
                user = User(user_data)
                message.user = user
            messages.append(message)
        return messages

    @classmethod
    def delete(cls, message_id):
        query = "DELETE FROM message_board WHERE id = %(id)s;"
        data = {'id': message_id}
        connectToMySQL(cls.db).query_db(query, data)

    def like(self):
        if self.like_count is None:
            self.like_count = 1
        else:
            self.like_count += 1
        if self.like_count < 0:
            self.like_count = 0
        query = "UPDATE message_board SET like_count = %(like_count)s WHERE id = %(id)s;"
        data = {'like_count': self.like_count, 'id': self.id}
        connectToMySQL(self.db).query_db(query, data)


    def unlike(self):
        if self.like_count > 0:
            self.like_count -= 1
        query = "UPDATE message_board SET like_count = %(like_count)s WHERE id = %(id)s;"
        data = {'like_count': self.like_count, 'id': self.id}
        connectToMySQL(self.db).query_db(query, data)
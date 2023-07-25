from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re
import requests
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    db = "wedding_schema"
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.street = data['street']
        self.city = data['city']
        self.zip_code = data['zip_code']
        self.state = data['state']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO users (first_name, last_name, email, password, street, city, zip_code, state)
        VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, %(street)s, %(city)s, %(zip_code)s, %(state)s);
        """
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def get_by_id(cls, user_id):
            query = "SELECT * FROM users WHERE id = %(user_id)s;"
            data = {
                'user_id': user_id
            }
            result = connectToMySQL(cls.db).query_db(query, data)
            if result:
                return cls(result[0])
            return None
        
    @classmethod
    def get_one(cls, user_id):
        query = "SELECT * FROM users WHERE user_id = %(user_id)s;"
        data = {'user_id': user_id}
        result = connectToMySQL(cls.db).query_db(query, data)
        if result:
            return cls(result[0])
        return None

    @classmethod
    def get_by_email(cls, email):
        query = """
        SELECT *
        FROM users
        WHERE email = %(email)s;
        """
        result = connectToMySQL(cls.db).query_db(query, {'email': email})
        if result:
            return cls(result[0])
        return None

    @staticmethod
    def validate_registration(data):
        is_valid = True
        if len(data['first_name']) < 1:
            flash("First name must be at least 1 character.")
            is_valid = False
        if len(data['last_name']) < 1:
            flash("Last name must be at least 1 character.")
            is_valid = False
        if not EMAIL_REGEX.match(data['email']):
            flash("Invalid email address!")
            is_valid = False
        if len(data['password']) < 8:
            flash("Password must be at least 8 characters.")
            is_valid = False
        return is_valid

    @staticmethod
    def validate_login(data):
        is_valid = True
        if len(data['email']) < 1:
            flash("Email field must not be empty.")
            is_valid = False
        if len(data['password']) < 1:
            flash("Password field must not be empty.")
            is_valid = False
        return is_valid

    def get_hotels(self):
        url = "https://apidojo-booking-v1.p.rapidapi.com/properties/list-by-map"
        # Convert the latitude and longitude to decimal degrees
        latitude = 39.050947
        longitude = -74.757942
        # Define the box size (adjust as needed)
        box_size = 0.1
        # Calculate the bounding box coordinates
        min_latitude = latitude - box_size
        max_latitude = latitude + box_size
        min_longitude = longitude - box_size
        max_longitude = longitude + box_size
        # Format the bbox parameter
        bbox = f"{min_longitude},{min_latitude},{max_longitude},{max_latitude}"
        querystring = {
            "arrival_date": "2024-09-20",
            "departure_date": "2024-10-01",
            "room_qty": "1",
            "guest_qty": "1",
            "bbox": bbox,
            "search_id": "none",
            "price_filter_currencycode": "USD",
            "categories_filter": "class::1,class::2,class::3",
            "languagecode": "en-us",
            "travel_purpose": "leisure",
            "children_qty": "0",
            "order_by": "popularity"
        }
        headers = {
            "X-RapidAPI-Key": "fbc5a93e38mshdd1e63c892e86efp1ce21djsnb5d259bd0fbf",
            "X-RapidAPI-Host": "apidojo-booking-v1.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        print(response.json())




from flask import render_template, redirect, request, session, flash
from flask_app import app
from flask_app.models.model_user import User
from flask_app.models.model_message import Message
from flask_app.models.model_seatingtable import Seatingtables
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route('/')
def start():
    return render_template('registration.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    
    user_id = session['user_id']
    user = User.get_by_id(user_id)
    table = Seatingtables.get_one_user_table(user_id)
    seat = Seatingtables.get_one_user_seat(user_id)
    guest_seat = Seatingtables.get_plus_one_seat(user_id)
    guests = []
    if guest_seat:
        guests = [{'seat': guest_seat}]
    messages = Message.get_all_messages()
    checkin_date = "2024-09-20"
    checkout_date = "2024-09-22"
    latitude = 39.054540
    longitude = -74.760680
    user.get_hotels()  # Call the get_hotels method
    hotel_data = []  # Modify this to store the hotel information
    return render_template('dashboard.html', user=user, table=table, seat=seat, guests=guests, guest_seat=guest_seat, messages=messages, hotels=hotel_data)


@app.route('/register', methods=['POST'])
def register():
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    if password != confirm_password:
        flash("Passwords do not match", "error")
        return redirect('/')
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')  # Encrypt password and decode it
    data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': pw_hash,
        'street': request.form['street'],
        'city': request.form['city'],
        'zip_code': request.form['zip_code'],
        'state': request.form['state']
    }
    if User.validate_registration(data):
        user_id = User.save(data)
        session['user_id'] = user_id
        flash("Registration successful. Please log in.", "success")
        return redirect('/login')
    else:
        return redirect('/')

@app.route('/login')
def login():
    return render_template('index.html')

@app.route('/login_user', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']
    data = {
        'email': email,
        'password': password
    }
    if User.validate_login(data):
        user = User.get_by_email(email)
        if user is None or not bcrypt.check_password_hash(user.password, password):
            flash("Invalid email or password. Please try again.", "error")
            return redirect('/login')
        session['user_id'] = user.id
        return redirect('/dashboard')
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect('/login')


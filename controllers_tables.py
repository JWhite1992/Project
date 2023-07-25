from flask import render_template, redirect, request, session, flash
from flask_app import app
from flask_app.models.model_seatingtable import Seatingtables
from flask_app.models.model_user import User

@app.route('/save_seat', methods=['POST'])
def save_seat():
    guest = 1 if request.form.get('plus_one') == 'on' else 0
    table_id = int(request.form.get('table_id') or 0)
    seat_id = int(request.form.get('seat_id') or 0)
    plus_one_seat_id = int(request.form.get('plus_one_seat_id') or 0)
    if 'user_id' in session:
        user_id = session['user_id']
        data = {
            'table': table_id,
            'seat': seat_id,
            'guest': guest,
            'user_id': user_id
        }
        result = Seatingtables.create(data)
        print("Seatingtables created:", result)
        # If the plus_one checkbox is checked, insert plus_one_seat_id as well
        if guest and plus_one_seat_id:
            plus_one_data = {
                'table': table_id,
                'seat': plus_one_seat_id,
                'guest': 1,  # Set guest to 1 for the plus one guest
                'user_id': user_id
            }
            plus_one_result = Seatingtables.create(plus_one_data)
            print("Plus one guest seat created:", plus_one_result)
        return redirect('/dashboard')
    else:
        flash('You must be logged in to select a seat.', 'error')
        return redirect('/login')


@app.route('/tables/and/seats', methods=['GET'])
def show_tables_and_seats():
    user_id = session.get('user_id')
    if user_id:
        table = Seatingtables.get_one_user_table(user_id)
        seat = Seatingtables.get_one_user_seat(user_id)
        if table and seat:
            flash('You have already selected a seat!')
            return redirect('/dashboard')
    tables = Seatingtables.get_all_tables_with_users()
    taken_tables = [table.id for table in tables if table.seat is not None]
    available_tables = [table for table in tables if table.id not in taken_tables]
    return render_template('seating_chart.html', tables=available_tables)


@app.route('/tables/<int:table_id>', methods=['GET'])
def show_table(table_id):
    table = Seatingtables.get_one_user_table(table_id)
    seat = Seatingtables.get_one_user_seat(table_id)
    if not table:
        return redirect('/tables')
    return render_template('seating_chart.html', tables=[table])


@app.route('/seats', methods=['GET'])
def show_seats():
    seats = Seatingtables.get_all_tables_with_users()
    taken_seats = [seat.seat for seat in seats if seat.seat is not None]
    available_seats = [seat for seat in seats if seat.seat not in taken_seats]
    return render_template('seating_chart.html', seats=available_seats)


@app.route('/seats/<int:user_id>/edit')
def edit_seat(user_id):
    user = User.get_one({'id': user_id})
    seat = Seatingtables.get_one_user_seat(user_id)
    guest_seat = Seatingtables.get_plus_one_seat(user_id)
    return render_template('edit_seat.html', user=user, seat=seat, plus_one_seat=guest_seat)


@app.route('/seats/<int:user_id>/update', methods=['POST'])
def update_seat(user_id):
    # Retrieve the seat data from the form submission
    table = request.form['table']
    seat = request.form['seat']
    unselect_seat = bool(request.form.get('unselect_seat'))
    add_plus_one = bool(request.form.get('add_plus_one'))
    guest_seat = request.form['guest'] if add_plus_one else None
    # Update the seating table record in the database
    data = {
        'user_id': user_id,
        'table': table,
        'seat': seat
    }
    Seatingtables.update(data)
    # Handle unselecting seat
    if unselect_seat:
        Seatingtables.delete_seat(user_id)
    # Handle adding plus one
    if add_plus_one and guest_seat:
        Seatingtables.add_plus_one(user_id, guest_seat)
    return redirect('/dashboard')



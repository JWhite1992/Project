from flask import render_template, redirect, request, session, flash
from flask_app import app
from flask_app.models.model_message import Message

@app.route('/messages')
def messages():
    messages = Message.get_all_messages()
    return render_template('dashboard.html', messages=messages)

@app.route("/messages/new")
def new_message():
    return render_template("add_message.html")

@app.route('/messages/edit/<int:message_id>', methods=['GET'])
def edit_message(message_id):
    message = Message.get_one_message_with_user(message_id)
    if not message:
        flash('Message not found', 'error')
        return redirect('/dashboard')
    if message.user_id != session.get('user_id'):
        flash('You are not authorized to edit this message', 'error')
        return redirect('/dashboard')
    return render_template('edit_message.html', message=message)

@app.route("/messages/update/<int:message_id>", methods=["POST"])
def update_message(message_id):
    data = {
        "id": message_id,
        "name": request.form["name"],
        "message": request.form["message"]
    }
    Message.update(data)
    flash('Message updated successfully!', 'success')
    return redirect("/dashboard")

@app.route("/messages/create", methods=["POST"])
def create_message():
    data = {
        "name": request.form["name"],
        "message": request.form["message"],
        "users_id": session["user_id"]
    }
    Message.create(data)
    return redirect("/dashboard")

@app.route('/messages/view/<int:message_id>')
def view_message(message_id):
    message = Message.get_one_message_with_user(message_id)
    return render_template("view_message.html", message=message)

@app.route('/messages/<int:message_id>/like', methods=['POST'])
def like_message(message_id):
    if 'user_id' not in session:
        flash('You must be logged in to like a message', 'error')
        return redirect('/dashboard')
    message = Message.get_one(message_id)
    if not message:
        flash('Message not found', 'error')
        return redirect('/dashboard')
    if message.user_id == session['user_id']:
        flash('You cannot like your own message', 'error')
        return redirect('/dashboard')
    message.like()
    flash('Message liked successfully!', 'success')
    return redirect('/dashboard')

@app.route('/messages/<int:message_id>/unlike', methods=['POST'])
def unlike_message(message_id):
    if 'user_id' not in session:
        flash('You must be logged in to unlike a message', 'error')
        return redirect('/dashboard')
    message = Message.get_one(message_id)
    if not message:
        flash('Message not found', 'error')
        return redirect('/dashboard')
    message.unlike()
    flash('Message unliked successfully!', 'success')
    return redirect('/dashboard')

@app.route('/messages/<int:message_id>/delete', methods=['POST'])
def delete_message(message_id):
    message = Message.get_one_message_with_user(message_id)
    if not message:
        flash('Message not found', 'error')
        return redirect('/dashboard')
    if message.user_id != session.get('user_id'):
        flash('You are not authorized to delete this message', 'error')
        return redirect('/dashboard')
    Message.delete(message_id)
    flash('Message deleted successfully!', 'success')
    return redirect('/dashboard')
    
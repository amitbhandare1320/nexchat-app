from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import db, User, Message, Room, RoomMember
from auth import auth_bp
from chat import chat_bp
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)

# Track online users
online_users = {}

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('chat.home'))

@socketio.on('connect')
def handle_connect():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            online_users[request.sid] = user.id
            user.is_online = True
            db.session.commit()
            emit('user_online', {'user_id': user.id, 'username': user.username}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in online_users:
        user_id = online_users.pop(request.sid)
        user = User.query.get(user_id)
        if user:
            user.is_online = False
            db.session.commit()
            emit('user_offline', {'user_id': user.id, 'username': user.username}, broadcast=True)

@socketio.on('join_room')
def handle_join_room(data):
    room = data.get('room')
    join_room(room)
    emit('status', {'msg': f'{session.get("username")} has joined the room.'}, to=room)

@socketio.on('leave_room')
def handle_leave_room(data):
    room = data.get('room')
    leave_room(room)
    emit('status', {'msg': f'{session.get("username")} has left the room.'}, to=room)

@socketio.on('send_message')
def handle_send_message(data):
    room = data.get('room')
    message_text = data.get('message')
    sender_id = session.get('user_id')
    sender_username = session.get('username')

    if not message_text or not sender_id:
        return

    # Save to DB
    msg = Message(
        sender_id=sender_id,
        room_name=room,
        content=message_text
    )
    db.session.add(msg)
    db.session.commit()

    emit('receive_message', {
        'sender': sender_username,
        'sender_id': sender_id,
        'message': message_text,
        'timestamp': msg.timestamp.strftime('%H:%M'),
        'room': room
    }, to=room)

@socketio.on('typing')
def handle_typing(data):
    room = data.get('room')
    emit('user_typing', {
        'username': session.get('username')
    }, to=room, include_self=False)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    room = data.get('room')
    emit('user_stop_typing', {
        'username': session.get('username')
    }, to=room, include_self=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import db, User, Message, Room, Reaction
from auth import auth_bp
from chat import chat_bp
from config import Config
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")
app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)

online_users = {}

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('chat.home'))
    return render_template('index.html')

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
            emit('user_offline', {'user_id': user.id}, broadcast=True)

@socketio.on('join_room')
def handle_join_room(data):
    room = data.get('room')
    join_room(room)
    emit('status', {'msg': f'{session.get("username")} joined.'}, to=room)

@socketio.on('leave_room')
def handle_leave_room(data):
    leave_room(data.get('room'))

@socketio.on('send_message')
def handle_send_message(data):
    room = data.get('room')
    message_text = data.get('message', '').strip()
    msg_type = data.get('msg_type', 'text')
    disappear_after = int(data.get('disappear_after', 0))
    sender_id = session.get('user_id')
    if not message_text or not sender_id:
        return
    msg = Message(sender_id=sender_id, room_name=room, content=message_text,
                  msg_type=msg_type, disappear_after=disappear_after)
    db.session.add(msg)
    db.session.commit()
    user = User.query.get(sender_id)
    emit('receive_message', {
        'id': msg.id,
        'sender': session.get('username'),
        'sender_id': sender_id,
        'avatar': user.get_photo_url() or user.avatar,
        'is_photo_avatar': bool(user.photo),
        'message': message_text,
        'msg_type': msg_type,
        'disappear_after': disappear_after,
        'timestamp': msg.timestamp.strftime('%H:%M'),
        'room': room,
        'reactions': {}
    }, to=room)

@socketio.on('message_seen')
def handle_message_seen(data):
    msg_id = data.get('msg_id')
    room = data.get('room')
    msg = Message.query.get(msg_id)
    if msg and msg.sender_id != session.get('user_id') and not msg.seen_at:
        msg.seen_at = datetime.utcnow()
        db.session.commit()
        emit('message_seen', {'msg_id': msg_id, 'disappear_after': msg.disappear_after}, to=room)

@socketio.on('delete_message')
def handle_delete_message(data):
    msg_id = data.get('msg_id')
    room = data.get('room')
    msg = Message.query.get(msg_id)
    if msg:
        msg.is_deleted = True
        msg.content = '🚫 This message was deleted'
        db.session.commit()
        emit('message_deleted', {'msg_id': msg_id}, to=room)

@socketio.on('react_message')
def handle_react(data):
    msg_id = data.get('msg_id')
    emoji = data.get('emoji')
    room = data.get('room')
    user_id = session.get('user_id')
    existing = Reaction.query.filter_by(message_id=msg_id, user_id=user_id).first()
    if existing:
        if existing.emoji == emoji:
            db.session.delete(existing)
        else:
            existing.emoji = emoji
    else:
        db.session.add(Reaction(message_id=msg_id, user_id=user_id, emoji=emoji))
    db.session.commit()
    msg = Message.query.get(msg_id)
    reaction_map = {}
    for r in msg.reactions:
        reaction_map[r.emoji] = reaction_map.get(r.emoji, 0) + 1
    emit('reactions_updated', {'msg_id': msg_id, 'reactions': reaction_map}, to=room)

@socketio.on('typing')
def handle_typing(data):
    emit('user_typing', {'username': session.get('username')}, to=data.get('room'), include_self=False)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    emit('user_stop_typing', {}, to=data.get('room'), include_self=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
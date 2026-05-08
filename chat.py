from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from models import db, User, Room, RoomMember, Message
from functools import wraps

chat_bp = Blueprint('chat', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@chat_bp.route('/home')
@login_required
def home():
    users = User.query.filter(User.id != session['user_id']).all()
    rooms = Room.query.filter_by(is_private=False).all()
    current_user = User.query.get(session['user_id'])
    return render_template('chat.html', users=users, rooms=rooms, current_user=current_user)

@chat_bp.route('/api/messages/<room_name>')
@login_required
def get_messages(room_name):
    messages = Message.query.filter_by(room_name=room_name)\
                            .order_by(Message.timestamp.asc())\
                            .limit(50).all()
    return jsonify([m.to_dict() for m in messages])

@chat_bp.route('/api/users')
@login_required
def get_users():
    users = User.query.filter(User.id != session['user_id']).all()
    return jsonify([u.to_dict() for u in users])

@chat_bp.route('/api/rooms', methods=['GET', 'POST'])
@login_required
def rooms():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()

        if not name:
            return jsonify({'error': 'Room name required'}), 400

        if Room.query.filter_by(name=name).first():
            return jsonify({'error': 'Room already exists'}), 400

        room = Room(name=name, description=description, created_by=session['user_id'])
        db.session.add(room)
        db.session.commit()
        return jsonify({'id': room.id, 'name': room.name, 'description': room.description})

    rooms = Room.query.filter_by(is_private=False).all()
    return jsonify([{'id': r.id, 'name': r.name, 'description': r.description} for r in rooms])

def get_private_room_name(user1_id, user2_id):
    ids = sorted([user1_id, user2_id])
    return f"private_{ids[0]}_{ids[1]}"

@chat_bp.route('/api/private/<int:user_id>')
@login_required
def get_private_room(user_id):
    room_name = get_private_room_name(session['user_id'], user_id)
    user = User.query.get_or_404(user_id)
    return jsonify({'room': room_name, 'user': user.to_dict()})

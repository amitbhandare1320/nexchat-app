from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, current_app
from models import db, User, Room, RoomMember, Message, Reaction
from functools import wraps
from werkzeug.utils import secure_filename
import os, uuid

chat_bp = Blueprint('chat', __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    current_user = User.query.get(session['user_id'])
    friends = current_user.friends_list.all()
    rooms = Room.query.filter_by(is_private=False).all()
    return render_template('chat.html', current_user=current_user, friends=friends, rooms=rooms)

@chat_bp.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    current_user = User.query.get(session['user_id'])
    user = User.query.get_or_404(user_id)
    is_friend = current_user.is_friend(user) if user.id != current_user.id else None
    return render_template('profile.html', user=user, current_user=current_user, is_friend=is_friend)

@chat_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    current_user = User.query.get(session['user_id'])
    if request.method == 'POST':
        data = request.get_json()
        action = data.get('action')
        if action == 'update_username':
            new_username = data.get('username', '').strip()
            if not new_username: return jsonify({'error': 'Username cannot be empty'}), 400
            if User.query.filter(User.username == new_username, User.id != current_user.id).first():
                return jsonify({'error': 'Username already taken'}), 400
            current_user.username = new_username
            session['username'] = new_username
            db.session.commit()
            return jsonify({'success': True})
        if action == 'update_bio':
            current_user.bio = data.get('bio', '')[:200]
            db.session.commit()
            return jsonify({'success': True})
        if action == 'update_avatar':
            current_user.avatar = data.get('avatar', '👤')
            session['avatar'] = current_user.avatar
            db.session.commit()
            return jsonify({'success': True})
        if action == 'update_theme':
            current_user.theme = data.get('theme', 'dark')
            session['theme'] = current_user.theme
            db.session.commit()
            return jsonify({'success': True})
        if action == 'update_status':
            current_user.status = data.get('status', 'online')
            db.session.commit()
            return jsonify({'success': True})
    return render_template('settings.html', current_user=current_user)

@chat_bp.route('/upload-photo', methods=['POST'])
@login_required
def upload_photo():
    current_user = User.query.get(session['user_id'])
    if 'photo' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['photo']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, filename))
    # Delete old photo
    if current_user.photo:
        old = os.path.join(upload_folder, current_user.photo)
        if os.path.exists(old): os.remove(old)
    current_user.photo = filename
    db.session.commit()
    return jsonify({'success': True, 'photo_url': f'/static/uploads/{filename}'})

@chat_bp.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['image']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"img_{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, filename))
    return jsonify({'success': True, 'url': f'/static/uploads/{filename}', 'filename': filename})

@chat_bp.route('/api/add-friend', methods=['POST'])
@login_required
def add_friend():
    data = request.get_json()
    nexchat_id = data.get('nexchat_id', '').strip().upper()
    current_user = User.query.get(session['user_id'])
    if nexchat_id == current_user.nexchat_id:
        return jsonify({'error': "You can't add yourself!"}), 400
    user = User.query.filter_by(nexchat_id=nexchat_id).first()
    if not user: return jsonify({'error': 'User not found'}), 404
    if current_user.is_friend(user): return jsonify({'error': 'Already friends!'}), 400
    current_user.add_friend(user)
    db.session.commit()
    return jsonify({'success': True, 'user': user.to_dict()})

@chat_bp.route('/api/remove-friend/<int:user_id>', methods=['POST'])
@login_required
def remove_friend(user_id):
    current_user = User.query.get(session['user_id'])
    user = User.query.get_or_404(user_id)
    current_user.remove_friend(user)
    db.session.commit()
    return jsonify({'success': True})

@chat_bp.route('/api/messages/<room_name>')
@login_required
def get_messages(room_name):
    messages = Message.query.filter_by(room_name=room_name, is_deleted=False)\
                            .order_by(Message.timestamp.asc()).limit(60).all()
    return jsonify([m.to_dict() for m in messages])

@chat_bp.route('/api/rooms', methods=['GET', 'POST'])
@login_required
def rooms():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        if not name: return jsonify({'error': 'Room name required'}), 400
        if Room.query.filter_by(name=name).first(): return jsonify({'error': 'Room already exists'}), 400
        room = Room(name=name, description=description, created_by=session['user_id'])
        db.session.add(room)
        db.session.commit()
        return jsonify({'id': room.id, 'name': room.name, 'description': room.description})
    rooms = Room.query.filter_by(is_private=False).all()
    return jsonify([{'id': r.id, 'name': r.name, 'description': r.description} for r in rooms])

@chat_bp.route('/api/private/<int:user_id>')
@login_required
def get_private_room(user_id):
    ids = sorted([session['user_id'], user_id])
    room_name = f"private_{ids[0]}_{ids[1]}"
    user = User.query.get_or_404(user_id)
    return jsonify({'room': room_name, 'user': user.to_dict()})

@chat_bp.route('/api/unread-counts')
@login_required
def unread_counts():
    current_user = User.query.get(session['user_id'])
    friends = current_user.friends_list.all()
    counts = {}
    for friend in friends:
        ids = sorted([current_user.id, friend.id])
        room_name = f"private_{ids[0]}_{ids[1]}"
        count = Message.query.filter_by(room_name=room_name, is_deleted=False)\
                             .filter(Message.sender_id != current_user.id)\
                             .filter(Message.seen_at == None).count()
        if count > 0:
            counts[str(friend.id)] = count
    return jsonify(counts)
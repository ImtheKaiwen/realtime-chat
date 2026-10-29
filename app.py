from flask import Flask, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import db, User, Message
from routes import main
from config import Config
import datetime

app = Flask(__name__)
app.config.from_object(Config)
if not app.config.get('SECRET_KEY'):
    raise RuntimeError('SECRET_KEY environment variable is required')
db.init_app(app)
app.register_blueprint(main)

# Socket.IO kurulumu
socketio = SocketIO(app, async_mode=app.config.get('SOCKETIO_ASYNC_MODE'))

# Socket.IO Event Handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_group')
def handle_join_group(data):
    group_id = data.get('group_id')
    if group_id and session.get('user_id'):
        join_room(f'group_{group_id}')
        print(f'User joined group {group_id}')

@socketio.on('leave_group')
def handle_leave_group(data):
    group_id = data.get('group_id')
    if group_id and session.get('user_id'):
        leave_room(f'group_{group_id}')
        print(f'User left group {group_id}')

@socketio.on('send_message')
def handle_send_message(data):
    content = data.get('content')
    group_id = data.get('group_id')
    user_id = session.get('user_id')
    
    if content and group_id and user_id:
        user = db.session.get(User, user_id)
        if user:
            new_message = Message(content=content, user_id=user_id, group_id=group_id)
            db.session.add(new_message)
            db.session.commit()
            
            # Mesajı tüm kullanıcılara gönder
            message_data = {
                'id': new_message.id,
                'content': content,
                'username': user.username,
                'group_id': group_id,
                'timestamp': datetime.datetime.now().isoformat()
            }
            emit('new_message', message_data, room=f'group_{group_id}')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    import os
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port)

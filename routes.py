from flask import Blueprint, render_template, request, session, jsonify
from models import User, db, Group,Message
import datetime
main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        # Kullanıcının üye olmadığı grupları al
        all_groups = Group.query.all()
        user_groups = user.groups
        other_groups = [group for group in all_groups if group not in user_groups]
        return render_template('chat.html', user=user, groups=other_groups)
    else:
        # Giriş yapmamış kullanıcılar için tüm grupları göster
        groups = Group.query.all()
        return render_template('index.html', groups=groups, user=None)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        
        if email and password:
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                db.session.commit()
                session['user_id'] = user.id
                return jsonify({"message": "Login successful", "success" : True}), 200
            else:
                return jsonify({"message": "Invalid credentials", "success" : False}), 401
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        
        if username and email and password:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"message": "User registered successfully","success" : True}), 201
    return render_template('register.html')

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    groups = Group.query.all()
    return render_template('index.html', groups=groups, user=None)

@main.route('/create_channel', methods=['POST'])
def create_channel():
    if 'user_id' in session:
        data = request.get_json()
        channel_name = data.get("channel_name")
        
        user = db.session.get(User, session['user_id'])

        if channel_name:
            new_group = Group(name=channel_name)
            new_group.members.append(user)
            db.session.add(new_group)
            db.session.commit()
            return jsonify({"message": "Channel created successfully", "success" : True}), 201
    return jsonify({"message": "Unauthorized", "success" : False}), 401



@main.route('/chat/<int:group_id>', methods=['GET'])
def chat(group_id):
    if 'user_id' in session:
        try:
            print(f"Session user_id: {session['user_id']}")
            print(f"Requested group_id: {group_id}")
            
            group = Group.query.get_or_404(group_id)
            print(f"Found group: {group.name}")
            
            user = db.session.get(User, session['user_id'])
            if not user:
                print("User not found in database")
                return jsonify({"message": "User not found", "success": False}), 404
            
            print(f"Found user: {user.username}")
            other_groups = [g for g in Group.query.all() if g.id != group.id]
            return render_template('group.html', group=group, user=user, other_groups=other_groups)
        except Exception as e:
            print(f"Error in chat route: {str(e)}")
            return jsonify({"message": f"Error: {str(e)}", "success": False}), 500
    else:
        print("No user_id in session")
        return jsonify({"message": "Unauthorized - No session", "success" : False}), 401

@main.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' in session:
        data = request.get_json()
        content = data.get("content")
        group_id = data.get("group_id")
        
        if content and group_id:
            user = db.session.get(User, session['user_id'])
            new_message = Message(content=content, user_id=session['user_id'], group_id=group_id)
            db.session.add(new_message)
            db.session.commit()
            
            return jsonify({"message": "Message sent successfully", "success" : True}), 201
    return jsonify({"message": "Unauthorized", "success" : False}), 401

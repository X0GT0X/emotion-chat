from flask import Flask, redirect
from flask_socketio import SocketIO, emit
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from database.db import initialize_db
from resources.routes import initialize_routes
from resources.errors import errors
from database.models import User, OnlineUser, Chat, Message, Group, Invitation
from resources.errors import InternalServerError
from time import time


app = Flask(__name__)

api = Api(app, errors=errors)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

app.debug = True
app.host = '0.0.0.0'

app.config['SECRET_KEY'] = 'mysecret'
app.config['JWT_SECRET_KEY'] = '73fbefb128dc0d0523ab794b508d81e8'
app.config['MONGODB_SETTINGS'] = {
    # 'host': 'mongodb://localhost/chat-app',
    'host': 'mongodb+srv://emotion-app:DMyKD8xCEUfSFYHC@cluster-rqa9o.gcp.mongodb.net/chat-app?retryWrites=true&w=majority'
}
app.config['UPLOAD_FOLDER'] = '/files/profile_images'

initialize_db(app)
initialize_routes(api)

socketIO = SocketIO(app, cors_allowed_origins="*")
CORS(app)


@socketIO.on("send_message")
def handle_message(data):
    try:

        timestamp = str(time()*1000)
        users_login = []
        if data['type'] == 'chat':
            chat = Chat.objects.get(chat_id=data['chat'])
            sender = User.objects.get(login=data['sender'])
            message_body = {
                'sender': sender,
                'message': data['message'],
                'chat': chat,
                'emotion': '',
                'timestamp': timestamp
            }

            message = Message(**message_body)
            message.save()

            for user in chat.users:
                users_login.append(user.login)

            chat.update(push__messages=message, set__lastUpdate=timestamp, set__receiverHasRead=False)
            chat.save()
        else:
            group = Group.objects.get(chat_id=data['chat'])
            sender = User.objects.get(login=data['sender'])
            message_body = {
                'sender': sender,
                'message': data['message'],
                'emotion': '',
                'timestamp': timestamp
            }

            message = Message(**message_body, chat=group)
            message.save()

            for user in group.users:
                users_login.append(user.login)

            receivers = [user for user in group.users if user != sender]

            group.update(push__messages=message, set__lastUpdate=timestamp, set__receiversHasReadList=receivers)
            group.save()

        emit('message_sent', {
            'message': 'Message was successfully sent.',
            'users': users_login,
            'chat': data['chat'],
            'sender': data['sender'],
        }, broadcast=True)
    except Exception as e:
        raise InternalServerError


@socketIO.on("remove_message")
def remove_message(data):
    try:
        message = Message.objects(id=data['message']).first()
        message.delete()

        users_login = []
        if data['type'] == 'chat':
            chat = Chat.objects(chat_id=data['chat']).first()
            last_message = chat.messages[-1]
            chat.update(set__lastUpdate=last_message.timestamp)
            chat.save()
            for user in chat.users:
                users_login.append(user.login)
        else:
            group = Group.objects(chat_id=data['chat']).first()
            last_message = group.messages[-1]
            group.update(set__lastUpdate=last_message.timestamp)
            group.save()
            for user in group.users:
                users_login.append(user.login)

        emit('message_removed', {
            'message': 'Message was successfully removed.',
            'users': users_login,
        }, broadcast=True)
    except Exception as e:
        raise InternalServerError


@socketIO.on("send_invitation")
def send_invitation(data):
    try:

        sender = User.objects.get(login=data['sender'])
        receiver = User.objects.get(login=data['receiver'])

        if Invitation.objects(sender=sender, receiver=receiver) or Invitation.objects(sender=receiver, receiver=sender):
            emit('invitation_error', {
                'error': 'You have already sent invitation to this user or you have got invitation.',
                'sender': data['sender'],
                'receiver': data['receiver'],
            }, broadcast=True)

        else:
            invitation_body = {
                'sender': sender,
                'receiver':receiver,
                'message': data['message'],
            }

            invitation = Invitation(**invitation_body)
            invitation.save()

            emit('invitation_sent', {
                'message': 'Your invitation was sent.',
                'sender': sender.login,
                'receiver': receiver.login,
            }, broadcast=True)
    except Exception as e:
        print(e)
        emit('invitation_error', {
            'error': 'Something went wrong.',
            'sender': data['sender'],
            'receiver': data['receiver'],
        }, broadcast=True)


@socketIO.on("accept_invitation")
def accept_invitation(data):
    try:

        sender = User.objects.get(login=data['sender'])
        receiver = User.objects.get(login=data['receiver'])

        sender.update(push__contacts=receiver)
        receiver.update(push__contacts=sender)

        sender.save()
        receiver.save()

        invitation = Invitation.objects.get(sender=sender, receiver=receiver)
        invitation.delete()

        emit('invitation_accepted', {
            'message': 'Invitation was accepted.',
            'sender': sender.login,
            'receiver': receiver.login,
        }, broadcast=True)
    except Exception as e:
        emit('invitation_error', {
            'error': 'Something went wrong.',
            'sender': data['sender'],
            'receiver': data['receiver'],
        }, broadcast=True)


@socketIO.on("decline_invitation")
def decline_invitation(data):
    try:

        sender = User.objects.get(login=data['sender'])
        receiver = User.objects.get(login=data['receiver'])

        invitation = Invitation.objects.get(sender=sender, receiver=receiver)
        invitation.delete()

        emit('invitation_declined', {
            'message': 'Invitation was declined.',
            'sender': sender.login,
            'receiver': receiver.login,
        }, broadcast=True)
    except Exception as e:
        emit('invitation_error', {
            'error': 'Something went wrong.',
            'sender': data['sender'],
            'receiver': data['receiver'],
        }, broadcast=True)


@socketIO.on("remove_chat")
def remove_chat(data):
    try:

        chat = Chat.objects(chat_id=data['chat_id']).first()
        users = chat.users
        users_login = []
        for user in users:
            users_login.append(user.login)
        chat.delete()

        emit('chat_removed', {
            'message': 'Chat was removed.',
            'users': users_login,
            'chat': data['chat_id']
        }, broadcast=True)
    except Exception as e:
        emit('remove_chat_error', {'error': 'Something went wrong.'}, broadcast=True)


@socketIO.on("remove_contact")
def remove_contact(data):
    try:
        if data['chat']:
            chat = Chat.objects(chat_id=data['chat']).first()
            chat.delete()

        users_login = [data['contact'], data['user']]
        contact = User.objects.get(login=data['contact'])
        current_user = User.objects.get(login=data['user'])

        contact.update(pull__contacts=current_user)
        contact.save()

        current_user.update(pull__contacts=contact)
        current_user.save()

        if data['chat']:
            emit('contact_removed', {
                'message': 'Contact was removed.',
                'users': users_login,
                'chat': data['chat']
            }, broadcast=True)
        else:
            emit('contact_removed', {
                'message': 'Contact was removed.',
                'users': users_login,
                'chat': ''
            }, broadcast=True)
    except Exception as e:
        print('111')
        print(str(e))
        emit('remove_contact_error', {'error': 'Something went wrong.'}, broadcast=True)


@socketIO.on("remove_group")
def remove_group(data):
    try:

        group = Group.objects(chat_id=data['chat_id']).first()
        users = group.users
        users_login = []
        for user in users:
            users_login.append(user.login)
        group.delete()

        emit('group_removed', {
            'message': 'Group was removed.',
            'users': users_login,
            'group': data['chat_id']
        }, broadcast=True)
    except Exception as e:
        emit('remove_group_error', {'error': 'Something went wrong.'}, broadcast=True)


@socketIO.on("leave_group")
def leave_group(data):
    try:

        group = Group.objects(chat_id=data['chat_id']).first()
        user = User.objects(login=data['user']).first()

        users_login = []
        for user_obj in group.users:
            users_login.append(user_obj.login)

        group.update(pull__users=user)
        if group.owner.login == data['user']:
            group.update(set__owner=group.users[0])
        group.save()

        emit('group_left', {
            'message': 'You have left the group.',
            'user': data['user'],
            'users': users_login,
            'group': data['chat_id']
        }, broadcast=True)
    except Exception as e:
        emit('leave_group_error', {
            'error': 'Something went wrong.',
            'user': data['user'],
        }, broadcast=True)


@socketIO.on("change_user_status")
def change_user_status(data):
    try:

        user_login = data['user']
        status = data['status']

        user = OnlineUser.objects(login=user_login).first()

        if status == 'online':
            if not user:
                user = OnlineUser(login=user_login)
                user.save()
        else:
            timestamp = str(time() * 1000)

            updated_user = User.objects(login=data['user']).first()
            updated_user.update(set__last_seen=timestamp)
            updated_user.save()

            user.delete()

        emit('user_status_changed', {'user': user_login}, broadcast=True)

    except Exception as e:
        emit('change_user_status_error', {'message': 'Something went wrong'}, broadcast=True)


@socketIO.on('chats_loading')
def load_chats():
    emit('chats_loaded')

@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/login')
def login():
    return redirect('/')


@app.route('/register')
def register():
    return redirect('/')


if __name__ == '__main__':
    socketIO.run(app, host='0.0.0.0')

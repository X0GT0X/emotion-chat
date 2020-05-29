from .db import db
from flask_bcrypt import generate_password_hash, check_password_hash


class User(db.Document):
    name = db.StringField(required=True)
    surname = db.StringField()
    login = db.StringField(required=True, min_length=6)
    password = db.StringField(required=True, min_length=6)

    profile_image = db.StringField()
    contacts = db.ListField(db.ReferenceField('User'), reverse_delete_rule=db.PULL)
    last_seen = db.StringField()

    def set_password(self, password):
        self.password = password

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    meta = {'collection': 'users'}


class OnlineUser(db.Document):
    login = db.StringField(required=True)

    meta = {'collection': 'online_users'}


class Invitation(db.Document):
    sender = db.ReferenceField('User', reverse_delete_rule=db.CASCADE, required=True)
    receiver = db.ReferenceField('User', reverse_delete_rule=db.CASCADE, required=True)
    message = db.StringField()

    meta = {'collection': 'invitations'}


class Chat(db.Document):
    chat_id = db.StringField()
    users = db.ListField(db.ReferenceField('User'), revese_delete_rule=db.CASCADE)
    receiverHasRead = db.BooleanField(required=True, default=False)
    messages = db.ListField(db.ReferenceField('Message'), reverse_delete_rule=db.PULL)
    lastUpdate = db.StringField()

    meta = {'collection': 'chats'}


class Message(db.Document):
    message = db.StringField(required=True)
    sender = db.ReferenceField('User', reverse_delete_rule=db.CASCADE, required=True)
    chat = db.GenericReferenceField()
    emotion = db.StringField()
    timestamp = db.StringField()

    meta = {'collection': 'messages'}


class Group(db.Document):
    chat_id = db.StringField()
    title = db.StringField()
    owner = db.ReferenceField('User', reverse_delete_rule=db.CASCADE, required=True)
    photo = db.StringField()
    users = db.ListField(db.ReferenceField('User'), reverse_delete_rule=db.PULL)
    messages = db.ListField(db.ReferenceField('Message'), reverse_delete_rule=db.PULL)
    lastUpdate = db.StringField()

    receiversHasReadList = db.ListField(db.ReferenceField('User'), reverse_delete_rule=db.PULL)

    meta = {'collection': 'groups'}


Chat.register_delete_rule(Message, 'chat', db.CASCADE)
Group.register_delete_rule(Message, 'chat', db.CASCADE)

Message.register_delete_rule(Chat, 'messages', db.PULL)
Message.register_delete_rule(Group, 'messages', db.PULL)

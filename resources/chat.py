from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import User, Chat, Group, Message
from time import time

from resources.errors import InternalServerError

import json
import os
import uuid


class ChatsApi(Resource):

    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        try:
            result = []
            chats = Chat.objects(users=user)
            for chat in chats:
                users = []

                for user in chat.users:
                    users.append({
                        'name': user.name,
                        'surname': user.surname,
                        'login': user.login,
                        'profile_image': user.profile_image,
                        'last_seen': user.last_seen,
                    })

                new_chat = {
                    'type': 'chat',
                    'chat_id': chat.chat_id,
                    'users': users,
                    'receiverHasRead': chat.receiverHasRead,
                    'messages': [],
                    'lastUpdate': chat.lastUpdate
                }
                for msg in chat.messages:

                    sender_user = User.objects.get(id=msg.sender.id)

                    sender = {
                        'name': sender_user.name,
                        'surname': sender_user.surname,
                        'login': sender_user.login,
                        'profile_image': sender_user.profile_image,
                        'last_seen': sender_user.last_seen,
                    }

                    message_body = {
                        'id': str(msg.id),
                        'message': msg.message,
                        'sender': sender,
                        'timestamp': msg.timestamp,
                        'emotion': msg.emotion
                    }
                    new_chat['messages'].append(message_body)

                result.append(new_chat)
            return Response(json.dumps(result), mimetype="application/json", status=200)
        except Exception as e:
            raise InternalServerError

    @jwt_required
    def post(self):
        try:

            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)

            body = request.get_json()
            users_login = [user.login, body.get('user')]

            if user.login == body.get('user'):
                return {'message': 'You cannot add chat with yourself.'}, 400

            if not User.objects(login=users_login[1]):
                return {'message': 'User with this login does not exists.'}, 400

            if Chat.objects(users=User.objects(login=body.get('login'))):
                return {'message': 'You already have chat with this user.'}, 400

            users = []

            for login in users_login:
                users.append(User.objects.get(login=login))

            chat_body = {
                'receiverHasRead': False,
                'users': users,
                'messages': [],
                'lastUpdate': str(time()*1000)
            }

            chat = Chat(**chat_body)
            chat.save()

            chat.chat_id = str(chat.id)
            chat.save()

            return {
                        'message': 'Chat was successfully created.',
                        'chat_id': chat.chat_id,
                   }, 200
        except Exception as e:
            print(e)
            return {'message': 'Something went wrong.'}, 400


class ChatApi(Resource):

    @jwt_required
    def put(self, chat_id):
        try:
            user_id = get_jwt_identity()
            if user_id:

                body = request.get_json()

                if(body.get('type') == 'group'):
                    group = Group.objects(chat_id=chat_id).first()
                    user = User.objects.get(id=user_id)
                    group.update(pull__receiversHasReadList=user)
                    group.save()
                else:
                    chat = Chat.objects(chat_id=chat_id).first()
                    chat.receiverHasRead = True
                    chat.save()

                return {'message': 'Receiver has read.'}, 200

            return {'message': 'Not authorized.'}, 403
        except Exception as e:
            return {'message': 'Something went wrong.'}, 400


class GroupsApi(Resource):

    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        try:
            result = []
            groups = Group.objects(users=user)
            for group in groups:
                users = []
                receivers = []

                for user in group.users:
                    user_object = User.objects.get(login=user.login)
                    users.append({
                        'name': user_object.name,
                        'surname': user_object.surname,
                        'login': user_object.login,
                        'profile_image': user_object.profile_image,
                        'last_seen': user.last_seen,
                    })

                for user in group.receiversHasReadList:
                    user_object = User.objects.get(login=user.login)
                    receivers.append({
                        'name': user_object.name,
                        'surname': user_object.surname,
                        'login': user_object.login,
                        'profile_image': user_object.profile_image,
                        'last_seen': user.last_seen,
                    })

                new_chat = {
                    'type': 'group',
                    'chat_id': group.chat_id,
                    'title': group.title,
                    'owner': group.owner.login,
                    'photo': group.photo,
                    'users': users,
                    'receivers': receivers,
                    'messages': [],
                    'lastUpdate': group.lastUpdate
                }

                for msg in group.messages:

                    sender_user = User.objects.get(id=msg.sender.id)

                    sender = {
                        'name': sender_user.name,
                        'surname': sender_user.surname,
                        'login': sender_user.login,
                        'profile_image': sender_user.profile_image,
                        'last_seen': sender_user.last_seen,
                    }

                    message_body = {
                        'id': str(msg.id),
                        'message': msg.message,
                        'sender': sender,
                        'timestamp': msg.timestamp,
                        'emotion': msg.emotion
                    }
                    new_chat['messages'].append(message_body)

                result.append(new_chat)
            return Response(json.dumps(result), mimetype="application/json", status=200)

        except Exception as e:
            raise InternalServerError

    @jwt_required
    def post(self):
        try:

            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)

            body = request.get_json()
            users_login = body.get('users')
            users_login.append(user.login)

            users = []

            for login in users_login:
                users.append(User.objects.get(login=login))

            group_body = {
                'title': body.get('title'),
                'owner': user,
                'users': users,
                'receiversHasReadList': [],
                'messages': [],
                'lastUpdate': str(time()*1000)
            }

            group = Group(**group_body)
            group.save()

            group.chat_id = str(group.id)
            group.save()

            return {'message': 'Group was successfully created.'}, 200
        except Exception as e:
            print(e)
            return {'message': 'Something went wrong.'}, 400


class GroupApi(Resource):

    @jwt_required
    def post(self, group_id):
        try:
            user_id = get_jwt_identity()
            if user_id:
                body = request.get_json()

                users = User.objects(login__in=body.get('users'))

                group = Group.objects(chat_id=group_id).first()
                group.update(set__users=users)
                group.save()

                return {'message': 'Group users were updated.'}, 200

            return {'message': 'Not authorized.'}, 403
        except Exception as e:
            print(e)
            return {'message': 'Something went wrong.'}, 400


class GroupImageApi(Resource):

    UPLOAD_FOLDER = 'static/files/group_images'

    @jwt_required
    def put(self, chat_id):
        user_id = get_jwt_identity()

        if user_id:
            try:

                group = Group.objects(chat_id=chat_id).first()

                file = request.files['file']
                filename, file_extension = os.path.splitext(file.filename)
                filename = str(uuid.uuid4()) + file_extension
                file.save(os.path.join(self.UPLOAD_FOLDER, filename))

                group.update(set__photo=('/' + os.path.join(self.UPLOAD_FOLDER, filename)))
                group.save()

                return {'message': 'Your photo was successfully uploaded.'}, 200
            except Exception as e:
                print(e)
                return {'message': 'Something went wrong.'}, 400

        return {'message': 'Not authorized.'}, 403

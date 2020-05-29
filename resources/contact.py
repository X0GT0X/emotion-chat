from flask import Response, request, jsonify
from database.models import User, Invitation, Chat
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
import json


class ContactsApi(Resource):

    @jwt_required
    def get(self):
        user_id = get_jwt_identity()

        if user_id:
            user = User.objects.get(id=user_id)
            contacts = user.contacts
            contact_list = []
            for contact in contacts:
                user = User.objects.get(id=contact.id)
                user_data = {
                    'name': user.name,
                    'surname': user.surname,
                    'login': user.login,
                    'profile_image': user.profile_image,
                    'last_seen': user.last_seen,
                }
                contact_list.append(user_data)
            return Response(json.dumps(contact_list), mimetype="application/json", status=200)

        return {'message': 'Not authorized.'}, 403

    @jwt_required
    def post(self):
        user_id = get_jwt_identity()

        if user_id:
            user = User.objects.get(id=user_id)
            contact = User.objects.get(login='test_login')
            user.update(push__contacts=contact)
            user.save()
            return {'message': 'Contact was added.'}, 201

        return {'message': 'Not authorized.'}, 403


class FilteredContactsApi(Resource):

    @jwt_required
    def get(self, login):
        user_id = get_jwt_identity()

        if user_id:
            current_user = User.objects.get(id=user_id)
            contacts = current_user.contacts

            exclude_users = []

            chats = Chat.objects(users=current_user)
            for chat in chats:
                for user in chat.users:
                    if user.login != current_user.login:
                        exclude_users.append(user.login)

            contact_list = []
            for contact in contacts:
                user = User.objects.get(id=contact.id)
                if user.login not in exclude_users:
                    contact_list.append(user.login)

            users = User.objects(login__startswith=login, login__in=contact_list).order_by('login').exclude('id', 'password')[:5]
            return Response(users.to_json(), mimetype="application/json", status=200)

        return {'message': 'Not authorized.'}, 403

    @jwt_required
    def delete(self, login):
        user_id = get_jwt_identity()

        try:
            if user_id:
                current_user = User.objects.get(id=user_id)
                contact = User.objects.get(login=login)

                chat = Chat.objects.get(users=[current_user, contact])
                chat.delete()

                current_user.update(pull_contacts=contact)
                current_user.save()

                return {'message': 'Contact was successfully removed.'}, 200

            return {'message': 'Not authorized.'}, 403
        except Exception as e:
            return {'message': 'Something went wrong.'}, 400


class InvitationsApi(Resource):

    @jwt_required
    def get(self):
        user_id = get_jwt_identity()

        if user_id:
            user = User.objects.get(id=user_id)
            sent_invitations = json.loads(Invitation.objects(sender=user).to_json())
            received_invitations = json.loads(Invitation.objects(receiver=user).to_json())

            received = []

            for invitation in received_invitations:
                sender = User.objects.get(id=invitation['sender']['$oid'])
                sender_data = {
                    'name': sender.name,
                    'surname': sender.surname,
                    'login': sender.login,
                    'profile_image': sender.profile_image,
                    'last_seen': sender.last_seen,
                }
                received.append({
                    'sender': sender_data,
                    'message': invitation['message']
                })

            return Response(json.dumps({'sent': sent_invitations, 'received': received}), mimetype="application/json", status=200)

        return {'message': 'Not authorized.'}, 403

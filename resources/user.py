from flask import Response, request
from database.models import User, OnlineUser
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
import os
import uuid


class UserApi(Resource):

    @jwt_required
    def get(self):

        user_id = get_jwt_identity()
        if user_id:
            user = User.objects.get(id=user_id)

            user_data = {
                'name': user.name,
                'surname': user.surname,
                'login': user.login,
                'profile_image': user.profile_image,
                'last_seen': user.last_seen,
            }

            return Response(json.dumps(user_data), mimetype="application/json", status=200)
        return {'message': 'Not authorized'}, 403

    @jwt_required
    def put(self):
        user_id = get_jwt_identity()
        if user_id:
            user = User.objects.get(id=user_id)

            body = request.get_json()

            if not body.get('password'):

                if user.login != body.get('login'):
                    check_login = User.objects(login=body.get('login'))
                    if check_login:
                        return {'message': 'User with this login already exists.'}, 400

                user.update(set__name=body.get('name'), set__surname=body.get('surname'), set__login=body.get('login'))
                user.save()

            else:
                check_password = user.check_password(body.get('password'))
                if check_password:
                    return {'message': 'You cannot use your old password.'}, 400
                else:
                    user.update(set__name=body.get('name'), set__surname=body.get('surname'),
                                set__login=body.get('login'))
                    user.set_password(body.get('password'))
                    user.hash_password()
                    user.save()

            user_data = {
                'name': user.name,
                'surname': user.surname,
                'login': user.login,
                'profile_image': user.profile_image,
                'last_seen': user.last_seen,
            }

            return {'message': 'Your account was successfully updated.', 'data': user_data}, 201

        return {'message': 'Not authorized.'}, 403


class UnauthorizedUserApi(Resource):

    def get(self, login):
        user = User.objects(login=login).exclude('id', 'password', 'login')
        print(user)
        if len(user) > 0:
            return Response(user[0].to_json(), mimetype="application/json", status=200)
        else:
            return {'message': 'This user does not exists.'}, 404


class FilteredUsersApi(Resource):

    @jwt_required
    def get(self, login):
        user_id = get_jwt_identity()

        if user_id:
            current_user = User.objects.get(id=user_id)
            exclude_users = [current_user.login]

            contacts = current_user.contacts
            for contact in contacts:
                exclude_users.append(contact.login)

            users = User.objects(login__startswith=login, login__nin=exclude_users).order_by('login').exclude('id', 'password')[:5]
            return Response(users.to_json(), mimetype="application/json", status=200)

        return {'message': 'Not authorized.'}, 403


class ProfileImageApi(Resource):

    UPLOAD_FOLDER = 'static/files/profile_images'

    @jwt_required
    def put(self):
        user_id = get_jwt_identity()

        if user_id:
            user = User.objects.get(id=user_id)

            try:
                file = request.files['file']
                filename, file_extension = os.path.splitext(file.filename)
                filename = str(uuid.uuid4()) + file_extension
                file.save(os.path.join(self.UPLOAD_FOLDER, filename))
                user.profile_image = '/' + os.path.join(self.UPLOAD_FOLDER, filename)
                user.save()

                user_data = {
                    'name': user.name,
                    'surname': user.surname,
                    'login': user.login,
                    'profile_image': user.profile_image,
                    'last_seen': user.last_seen,
                }

                return {'message': 'Your photo was successfully uploaded.',
                        'data': user_data}, 200
            except Exception as e:
                return {'message': 'Something went wrong.'}, 400

        return {'message': 'Not authorized.'}, 403


class OnlineUserApi(Resource):

    @jwt_required
    def get(self, login):
        user_id = get_jwt_identity()

        if user_id:

            user = User.objects.get(login=login)

            try:

                online_user = OnlineUser.objects(login=user.login).first()

                if online_user:
                    return {'online': True}, 200
                else:
                    return {'online': False}, 200
            except Exception as e:
                return {'message': 'Something went wrong.'}, 400

        return {'message': 'Not authorized.'}, 403

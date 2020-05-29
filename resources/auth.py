from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from database.models import User
import datetime

from mongoengine.errors import FieldDoesNotExist, NotUniqueError, DoesNotExist
from resources.errors import SchemaValidationError, UnauthorizedError, InternalServerError


class SignupApi(Resource):

    def post(self):
        try:
            body = request.get_json()
            login = body.get('login')

            # Check if user already exists
            user_db = User.objects(login=login)
            if(user_db):
                return {'error': 'User with that login already exists'}, 403

            user = User(**body)
            user.hash_password()
            user.save()

            expires = datetime.timedelta(days=7)
            access_token = create_access_token(identity=str(user.id), expires_delta=expires)
            return {'token': access_token}, 200

        except FieldDoesNotExist:
            raise SchemaValidationError
        except NotUniqueError:
            return {'error': 'User with that login already exists'}, 403
        except Exception as e:
            raise InternalServerError


class SigninApi(Resource):

    def post(self):
        try:
            body = request.get_json()
            user = User.objects.get(login=body.get('login'))
            authorized = user.check_password(body.get('password'))

            if not authorized:
                return {'error': 'Login or password invalid'}, 401

            expires = datetime.timedelta(days=365)
            access_token = create_access_token(identity=str(user.id), expires_delta=expires)
            return {'token': access_token}, 200
        except (UnauthorizedError, DoesNotExist):
            return {'error': 'Invalid login or password'}, 401
        except Exception as e:
            raise InternalServerError


class VerifyApi(Resource):

    @jwt_required
    def post(self):
        try:
            user_id = get_jwt_identity()

            if user_id:
                return {'token_is_valid': True}, 200
            else:
                return {'token_is_valid': False}, 403
        except UnauthorizedError:
            return {'token_is_valid': False}, 403

from flask_restful import Resource, Api, reqparse
from flask import Blueprint, request
from models import *
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

api_bp = Blueprint('user_api', __name__)
api = Api(api_bp)


def validate_blacklist(func):
    '''
    Validating token before work
    '''

    def wrapper(*args, **kwargs):
        if 'Authorization' in request.headers:
            identity = get_jwt_identity()
            identity_to_check = dict(hash=identity)
            if BlackListToken.validate_blacklist(hash=identity_to_check):
                return func(*args, **kwargs)
            else:
                return dict(response=f'Token invalid, need valid token first!'), 200
        else:
            return dict(response='Authorization Token Needed'), 501

    return wrapper


class User(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=False)
        self.parser.add_argument('password', type=str, required=False)
        self.parser.add_argument('type', type=str, required=False)

    def get(self):
        return {'Method': 'GET Not Implemented'}, 501

    def put(self):
        return {'Method': 'PUT Not Implemented'}, 501

    def delete(self):
        return {'Method': 'DELETE Not Implemented'}, 501

    def get_usn_pswd(self):
        data = self.parser.parse_args()
        return data['name'], data['password'], data['type']


class UserAPI(User):
    def __init__(self):
        User.__init__(self)

    def post(self, facility=None):
        '''
        return non-importaant info about user-
        :param facility: - assumes request is facility independent
        :return: - whether or not user exists
        '''
        data = self.parser.parse_args()
        name = (data['name'])
        query_user = userData.query.filter(userData.name == name).first()
        if query_user is not None:
            # if not valid request
            user_data = query_user._asdict()
            return user_data,  202
        elif query_user is None:
            return {
                       'user': 'Not found, please sign up'
                   }, 204

    @jwt_required
    def put(self, facility=None):
        '''
        create useres-using the put function
        :param facility: -->required only if a new user is to be created.
        :return:
        '''
        identity = get_jwt_identity()
        if identity.get('type') != "admin":
            return {'message': "You do not have access to create a user"}, 500
        data = self.parser.parse_args()
        name, password, type = (data.get('name'), data.get('password'), data.get('type'))
        if facility is not None and ((name and password and type) is not None):
            if userData.query.filter(userData.name == data.get('name')).first() is not None:
                return {'user': 'already exists'}, 201
            else:
                facility_ref = facilityData.query.filter(facilityData.facility_name == facility).first()
                data['facility_id'] = facility_ref.id
                new_user = userData(data)
                new_user.save()
                return {'user': f'Created {new_user.get(name)}'}, 201
        elif facility is None:
            return {
                       'error': 'Missing arguments, needs facility, name, password, and type'
                   }, 204

    @jwt_required
    def delete(self, facility=None):
        identity = get_jwt_identity()
        if identity.get('type') != "admin":
            return {'message': "You do not have access to delete a user"}, 500
        data = self.parser.parse_args()
        name, password, type = (data.get('name'), data.get('password'), data.get('type'))
        user_to_delete = userData.query.filter(userData.name == name).first()
        if facility is not None and ((name) is not None):
            if user_to_delete is not None:
                user_to_delete.delete()
                return {'user': 'Will Be Deleted'}, 202
        else:
            return dict(
                user=f'Resubmit with facility, and name with correct privileges'
            ), 202


class UsersList(User):
    def __init__(self):
        User.__init__(self)

    def get(self, facility=None):
        if facility is None:
            # todo need to add code for looking up user and responding with facility
            users_list = userData.query.all()
            return dict(users=[user._asdict() for user in users_list]), 201

        elif facility:
            _facility = facilityData.query.filter(facilityData.facility_name == facility).first()
            if facility is None:
                return dict(
                    user=f'Invalid Facility'
                ), 201
            else:
                users_list = _facility.users
                return dict(
                    users=[user._asdict for user in users_list]
                ), 201


class UserAuthLogin(User):
    def __init__(self):
        User.__init__(self)

    def post(self):
        usn, pswd, typeof = self.get_usn_pswd()
        if (usn is not None) and (pswd is not None):
            user = userData.query.filter(userData.name == usn).first()
            if user is None:
                return {'user': 'Not found please contact admin to sign you up'}
            else:
                user_dict = dict(usn=user.name, type=user.type)
                token = create_access_token(identity=user_dict)
                user.auth_hash = str(user_dict)
                user.save()
                return dict(access_token=token), 200
        else:
            return {'user': 'Please enter username and password'}

    @validate_blacklist
    @jwt_required
    def get(self):
        identity = get_jwt_identity()
        id = dict(name=identity['usn'], type=identity['type'])
        return id, 200


class UserAuthLogout(User):
    def __init__(self):
        User.__init__(self)

    @validate_blacklist
    @jwt_required
    def post(self):
        identity = get_jwt_identity()
        user_identity = identity.get('usn')
        user = userData.query.filter(userData.name == user_identity).first()
        if user is None:
            return dict(
                user=f'User {user_identity} does not exist'
            ), 201
        else:
            old_hash = dict(
                hash=user.auth_hash
            )
            blacklist = BlackListToken(data=old_hash)
            blacklist.save()
            user.auth_hash = None


api.add_resource(UserAPI, '/user', '/user/<string:facility>')
api.add_resource(UsersList, '/users', '/users/<string:facility>')
api.add_resource(UserAuthLogin, '/user/login')
api.add_resource(UserAuthLogout, '/user/logout')

# TODO need to test this out

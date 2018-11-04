from flask_restful import Resource, Api, reqparse
from flask import Blueprint
from models import *
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


api_bp = Blueprint('user_api', __name__)
api = Api(api_bp)


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

    def get(self, facility=None):
        data = self.parser.parse_args()
        name, password = (data['name'], data['password'])
        query_user = userData.query.filter(userData.name == name).first()
        if query_user is not None:
            #if not valid request
            user_data = query_user._asdict()
            return {
                'user': user_data['name'],
                'facility': user_data['facility']
            }, 202
        elif query_user is None:
            return {
                'user': 'Not found, please sign up'
            }, 204

    @jwt_required
    def put(self, facility=None):
        identity = get_jwt_identity()
        if identity.get('type') != "admin":
            return {'message': "You do not have access to create users"}, 500
        data = self.parser.parse_args()
        name, password, type = (data.get('name'), data.get('password'), data.get('type'))
        if facility is not None and ((name or password or type) is not None):
            if userData.query.filter(userData.name == data.get('name')).first() is not None:
                return {'user': 'already exists'}, 201
            else:
                facility_ref = facilityData.query.filter(facilityData.facility_name == facility).first()
                new_user = userData(data)
                new_user.facility_id = facility_ref.id
                new_user.save()
                return {'user': 'not found will create one'}, 201
        elif facility is None:
            return {
                'error': 'Missing arguments, needs facility, name, password, and type'
            }, 204

    def delete(self, facility=None):
        data = self.parser.parse_args()
        name, password, type = (data.get('name'), data.get('password'), data.get('type'))
        user_to_delete = userData.query.filter(userData.name == name).first()
        if facility is not None and ((name or password or type) is not None):
            if user_to_delete is not None:
                user_to_delete.delete()
                return {'user': 'Will Be Deleted'}, 202


class UsersList(User):
    def __init__(self):
        User.__init__(self)

    def get(self, facility=None):
        if facility is None:
            #todo need to add code for looking up user and responding with facility
            users_list = userData.query.all()
            return {'users':
                     [user._asdict() for user in users_list]}, 200


class UserAuth(User):
    def __init__(self):
        User.__init__(self)

    def post(self):
        usn, pswd, typeof = self.get_usn_pswd()
        if (usn is not None) and (pswd is not None):
            user = userData.query.filter(userData.name == usn).first()
            if user is None:
                return {'user': 'Not found please sign up'}
            else:
                user_dict = dict(usn=user.name, type=user.type)
                token = create_access_token(user_dict)
                user.auth_hash = token
                user.save()
                return dict(access_token=token), 200
        else:
            return {'user': 'Please enter username and password'}
    @jwt_required
    def get(self):
        identity = get_jwt_identity()
        id = dict(name=identity['usn'], type=identity['type'])
        return id, 200


api.add_resource(UserAPI, '/user/<string:facility>')
api.add_resource(UsersList, '/users', '/users/<string:facility>')
api.add_resource(UserAuth, '/user/login')


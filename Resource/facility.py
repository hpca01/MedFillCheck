from flask_restful import Resource, Api, reqparse
from models import facilityData
from flask import Blueprint
from functools import wraps, partial
from flask_jwt_extended import jwt_required, get_jwt_identity
from .users import validate_blacklist, admin_required

api_bp_facility = Blueprint('facility_api', __name__)
api = Api(api_bp_facility)
class NullFacilityException(Exception):
    '''Exception that is raised when facility is invalid'''
    def __init__(self, message, payload=None):
        self.message=message
        self.payload=payload
    def __str__(self):
        return str(self.message)

class InvalidFacilityException(Exception):
    '''Exception that is raised when facility is invalid'''
    def __init__(self, message, payload=None):
        self.message=message
        self.payload=payload
    def __str__(self):
        return str(self.message)

def validate_facility(facility_name=None):
    '''checks to see if the facility is valid and returns it if it is otherwise returns false'''
    if facility_name is None:
        raise NullFacilityException("Facility cannot be none")
    elif facility_name is not None:
        facility_obj:facilityData = facilityData.query.filter(facilityData.facility_name == facility_name).first()
        if facility_obj is None:
            raise InvalidFacilityException("Invalid facility")
        else:
            return facility_obj

def facility_validation_wrapper(func):
    @wraps(func)
    def run(*args, **kwargs):
        facility:str = kwargs.get("facility")
        if facility is None:
            return dict(error=f"Facility cannot be none for this function")
        else:
            facility_obj: facilityData = facilityData.query.filter(facilityData.facility_name == facility).first()
            if facility_obj is None:
                return dict(error=f'Facility {facility} does not exist in db, please contact admin')
            else:
                kwargs['facility_ob'] = facility_obj
                return partial(func, args, kwargs)
    return run

class FacilityResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('facility_name', type=str, required=False)

    def get(self):
        return {'Method': 'GET Not Implemented'}, 501

    def put(self):
        return {'Method': 'PUT Not Implemented'}, 501

    def delete(self):
        return {'Method': 'DELETE Not Implemented'}, 501

    def get_facility(self):
        data = self.parser.parse_args()
        return data['facility_name']

class FacilityList(FacilityResource):
    def __init__(self):
        FacilityResource.__init__(self)

    def get(self):
        '''list of facilities that are on the server'''
        facilitylist = facilityData.query.all()
        if facilitylist is None:
            return {"facilities": "No facilities registered"}, 201
        else:
            return {"facilities": [facility._asdict() for facility in facilitylist]}


class Facility(FacilityResource):
    def __init__(self):
        FacilityResource.__init__(self)
        self.facility_name = self.get_facility()

    @jwt_required
    @validate_blacklist
    def get(self, facilityname=None):
        if facilityname is None:
            return {
                "response" : "Please indicate facility name for GET method"
            }, 401
        facility = facilityData.query.filter(facilityData.facility_name == facilityname).first()
        if facility is not None:
            return {"facility": facility._asdict()}, 201
        else:
            return {"facility" : "facility not found"},201

    @jwt_required
    @admin_required
    @validate_blacklist
    def put(self, facilityname=None):
        if facilityname is not None:
            return {"response" : "method not allowed"}, 401
        data=dict()
        data['facility_name'] = self.facility_name
        dup_facility = facilityData.query.filter(facilityData.facility_name == self.facility_name).first()
        if dup_facility is None:
            new_facility = facilityData(data)
            new_facility.save()
            return {
                "facility" : "created {}".format(self.facility_name)
            }, 201
        else:
            return {
                "facility" : "Cannot create facility, it is a duplicate"
            }, 201

    @jwt_required
    @admin_required
    @validate_blacklist
    def delete(self, facilityname=None):
        if facilityname is not None:
            return {"response" : "method not allowed"}, 401
        facility = facilityData.query.filter(facilityData.facility_name == self.facility_name).first()
        if facility is not None:
            facility.delete()
            return {"facility": "deleted {}".format(self.facility_name)}
        else:
            return {
                "facility": "facility not found {}".format(self.facility_name)
            }, 201




api.add_resource(FacilityList, '/facilities/all')
api.add_resource(Facility, '/facility', '/facility/<string:facilityname>')
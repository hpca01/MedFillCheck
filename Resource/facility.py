from flask_restful import Resource, Api, reqparse
from models import facilityData
from flask import Blueprint

api_bp_facility = Blueprint('facility_api', __name__)
api = Api(api_bp_facility)

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
api.add_resource(Facility, '/facility', '/facility/<facilityname>')
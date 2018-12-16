from flask_restful import Resource, Api, reqparse
from models import facilityData, userData, MedstationData
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from .users import validate_blacklist, admin_required
from .facility import validate_facility, facility_validation_wrapper, NullFacilityException, InvalidFacilityException
import typing

api_bp_inventory = Blueprint('inventory_api', __name__)
api = Api(api_bp_inventory)


class InventoryResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('med_description', type=str, required=False)
        self.parser.add_argument('medid', type=str, required=False)
        self.parser.add_argument('min', type=int, required=False)
        self.parser.add_argument('max', type=int, required=False)
        self.parser.add_argument('current', type=int, required=False)
        self.parser.add_argument('pick_amount', type=int, required=False)
        self.parser.add_argument('checked', type=str, required=False)
        self.parser.add_argument('station_name', type=str, required=False)
        self.parser.add_arguments('refills', action='append', required=False)


    def get(self):
        return {'Method': 'GET Not Implemented'}, 501

    def put(self):
        return {'Method': 'PUT Not Implemented'}, 501

    def delete(self):
        return {'Method': 'DELETE Not Implemented'}, 501

    def get_station(self):
        data = self.parser.parse_args()
        return data


class InventoryList(InventoryResource):
    def __init__(self):
        InventoryResource.__init__(self)

    @jwt_required
    @validate_blacklist
    def get(self):
        '''
        to include refill list, user token required
        utility methods, get identity->get facility->get stations->get inventory
        :return: json with refill list of all the stations in a facility
        '''
        identity = get_jwt_identity()
        usn: str = identity.get('usn')
        user: userData = userData.query.filiter(userData.name == usn).first()
        user_facility = user.facility
        #todo need to get user facility then get inventory list from there
        try:
            facility:facilityData = validate_facility(user_facility)
        except NullFacilityException as e:
            return dict(error=f'User {usn} does not have a facility assigned')
        except InvalidFacilityException as e:
            return dict(error=f'User {usn} has an invalid facility {user_facility}')
        #todo write code to get inventory data from each of the stations
        output=[]
        for each_station in facility.stations:
            output.append(each_station._refill_list_as_dict())
        return output, 200
        #todo need to validate w/ actual data, gotta make a post method first

    @jwt_required
    @validate_blacklist
    def put(self): #todo create a post method to append a csv refill list to the get
        pass




# Todo add inventory resource
# api.add_resource(StationList, '/station/<string:facility>')

from flask_restful import Resource, Api, reqparse, inputs
from models import facilityData, userData, MedstationData, InventoryData
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .users import validate_blacklist, admin_required
from .facility import validate_facility, facility_validation_wrapper, NullFacilityException, InvalidFacilityException
from Schema import RefillData, RefillList
from marshmallow import UnmarshalResult, pprint


api_bp_inventory = Blueprint('inventory_api', __name__)
api = Api(api_bp_inventory)

class InventoryResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('station_name', type=str, help='Need station name')
        self.parser.add_argument('refills', action='append', type=dict, help='Need refill List')

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
        user: userData = userData.query.filter(userData.name == usn).first()
        #this doesn't return string, it returns facilityData obj
        user_facility = user.facility
        try:
            facility: facilityData = validate_facility(user_facility)
        except NullFacilityException as e:
            return dict(error=f'User {usn} does not have a facility assigned')
        except InvalidFacilityException as e:
            return dict(error=f'User {usn} has an invalid facility {user_facility}')
        output = []
        for each_station in facility.stations:
            output.append(each_station._refill_list_as_dict())
        return dict(facility=facility.facility_name, refills=output), 200

    #todo add decorators for identity and security
    @jwt_required
    @validate_blacklist
    def put(self):
        refills = RefillList()
        refill_data_schema = RefillData()
        usn:str = get_jwt_identity().get('usn')
        user:userData = userData.query.filter(userData.name == usn).first()
        data = request.get_json()
        refill_data :UnmarshalResult[RefillList] = refills.load(data)
        station_name=refill_data.data.get('station_name')
        medstation:MedstationData = MedstationData.query.filter(MedstationData.station_name == station_name).first()
        medstation_facility : facilityData = medstation.facility
        users_facility : userData = medstation_facility.users
        if user in users_facility:
            output=[]
            for each in refill_data.data['refills']:
                data, error=refill_data_schema.load(each)
                output.append(data)
                inv:InventoryData=InventoryData(data)
                inv.update(dict(station_id=medstation.id))
                inv.save()
        else:
            return dict(error=f'User is not registered to {medstation_facility.facility_name}'), 400
        return dict(status=f'Added to List {station_name}', values=output), 200



api.add_resource(InventoryList, '/refill_list')

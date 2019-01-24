from flask_restful import Resource, Api, reqparse
from models import MedstationData, facilityData
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from .facility import validate_facility, NullFacilityException, InvalidFacilityException
from .users import validate_blacklist, admin_required

api_bp_station = Blueprint('station_api', __name__)
api = Api(api_bp_station)


def check_station_unique(station_name=None):
    '''returns true if unique, false if not'''
    if station_name is None:
        return dict(station='Station name is required'), 401
    elif station_name:
        station = MedstationData.query.filter(MedstationData.station_name == station_name).first()
        if station is None:
            return True
        else:
            return False


class StationResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('station_name', type=str, required=False)

    def get(self):
        return {'Method': 'GET Not Implemented'}, 501

    def put(self):
        return {'Method': 'PUT Not Implemented'}, 501

    def delete(self):
        return {'Method': 'DELETE Not Implemented'}, 501

    def get_station(self):
        data = self.parser.parse_args()
        return data


class StationList(StationResource):
    def __init__(self):
        StationResource.__init__(self)

    def get(self, facility=None):
        try:
            facility_to_return: facilityData = validate_facility(facility)
        except NullFacilityException:
            return dict(error='Facility cannot be none'), 400
        except InvalidFacilityException as e:
            return dict(error=e.message), 400
        return facility_to_return._asdict(), 201

    @jwt_required
    @admin_required
    @validate_blacklist
    def put(self, facility=None):
        identity = get_jwt_identity()
        if identity['type'] != 'admin':
            return dict(station='You do not have admin privileges'), 400
        try:
            facility_to_return: facilityData = validate_facility(facility)
        except NullFacilityException:
            return dict(error=f'Facility cannot be none'), 400
        except InvalidFacilityException as e:
            return dict(error=e.message), 400
        data = self.get_station()
        station_name = data.get('station_name', None)
        if check_station_unique(station_name):
            new_station = MedstationData(data)
            new_station.facility_id = facility_to_return.id
            new_station.save()
            return dict(station=f'Created {station_name} for facility {facility_to_return.facility_name}'), 200
        else:
            return dict(
                station=f'Station {station_name} is not unique for facility {facility_to_return.facility_name}'), 200

    @jwt_required
    @admin_required
    @validate_blacklist
    def delete(self, facility=None):
        identity = get_jwt_identity()
        if identity['type'] != 'admin':
            return dict(station='You do not have admin privileges'),401
        try:
            facility_to_return: facilityData = validate_facility(facility)
        except NullFacilityException:
            return dict(error='Facility cannot be none'), 400
        except InvalidFacilityException as e:
            return dict(error=e.message), 400
        data = self.get_station()
        station_name = data.get('station_name', None)
        if check_station_unique(station_name):
            return dict(station=f'{station_name} does not exist'), 401
        else:
            _station:MedstationData = MedstationData.query.filter(MedstationData.station_name == station_name).first()
            facility_to_return.stations.remove(_station).save()
            _station.delete()
            return dict(station=f'Station {station_name} deleted from {facility_to_return.facility_name}'), 200

api.add_resource(StationList, '/station/<string:facility>')

#  api.add_resource(Facility, '/facility', '/facility/<string:facility>')

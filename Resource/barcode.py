from flask_restful import Resource, Api, reqparse
from models import barcodeData
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from .users import validate_blacklist

api_bp = Blueprint('api', __name__)
api = Api(api_bp)


parser = reqparse.RequestParser()
parser.add_argument('barcode', type=str)
parser.add_argument('medid', type=str)
parser.add_argument('user', type=str)


class BarcodeAPI(Resource):

    def get(self, id=None):
        items = barcodeData.query.all()
        output = [item._asdict() for item in items]
        return {'barcodes':output}, 201

    @validate_blacklist
    @jwt_required
    def put(self, id):
        data = parser.parse_args()
        #todo need to add code for querying barcodes
        new_barcode = barcodeData(data=data)
        new_barcode.save()
        print(new_barcode)
        return {'data': '{}'.format(id)}, 201

    def delete(self, id):
        pass


api.add_resource(BarcodeAPI, '/barcode/<int:id>')
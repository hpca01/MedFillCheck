from flask_restful import Resource, Api, reqparse
from Resource import make_error
from models import barcodeData
from flask_restful import abort, HTTP_STATUS_CODES
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from .users import validate_blacklist, admin_required

api_bp = Blueprint('api', __name__)
api = Api(api_bp)


parser = reqparse.RequestParser()
parser.add_argument('barcode', type=str)
parser.add_argument('medid', type=str)

def check_unqiue(barcode):
    '''
    :param barcode: barcode that you want to check for uniqueness
    :return: true if unique else false, default return is false
    '''
    if barcode:
        data = barcodeData.query.filter(barcodeData.barcode==barcode).first()
        if data:
            return False
        else:
            return True

class BarcodeAPI(Resource):

    def get(self, id=None):
        items = barcodeData.query.all()
        output = [item._asdict() for item in items]
        return {'barcodes':output}, 201

    @jwt_required
    @admin_required
    @validate_blacklist
    def put(self, id):
        data = parser.parse_args()
        #todo need to add code for querying barcodes
        if check_unqiue(id):
            new_barcode = barcodeData(data=data)
            new_barcode.save()
            return {'data': '{}'.format(id)}, 201
        else:
            return make_error(404, message='Not unique entry', action='Submit a non-duplicate entry')

    @jwt_required
    @admin_required
    @validate_blacklist
    def delete(self, id=None):
        if id is None:
            return abort(http_status_code=405,description='Method requires a barcode')
        else:
            barcode_to_delete:barcodeData = barcodeData.query.filter(barcodeData.barcode == id).first()
            if barcode_to_delete is None:
                return make_error(404, message="Barcode does not exist", action='Re-submit')
            barcode=barcode_to_delete.barcode
            barcode_to_delete.delete()
            return dict(deleted=barcode), 201




api.add_resource(BarcodeAPI, '/barcode/<int:id>')

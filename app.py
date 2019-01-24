'''
minimal api
'''

from flask import Flask, jsonify
from flask_marshmallow import Marshmallow
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from flask_migrate import Migrate
from config import app_config
from extensions import db, jwt, ma
import start_script

app = Flask(__name__)

app.config.from_object(app_config['development'])

jwt.init_app(app)
db.init_app(app)
ma.init_app(app)

Migrate(app=app, db=db)
import models
from Resource.barcode import api_bp
from Resource.users import api_bp as api
from Resource.facility import api_bp_facility
from Resource.station import api_bp_station
from Resource.inventory import api_bp_inventory


app.register_blueprint(api_bp_inventory)
app.register_blueprint(api_bp_station)
app.register_blueprint(api_bp_facility)
app.register_blueprint(api_bp)
app.register_blueprint(api)

if __name__ == '__main__':
    app.run(debug=True)

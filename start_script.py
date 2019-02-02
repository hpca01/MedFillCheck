
from models import *
import app
from extensions import db


def create_admin():
    '''
    create facility then create a user.
    :return:
    '''
    with app.app_context():
        db.create_all()
        fac1 = facilityData(dict(facility_name='RWC'))
        fac2 = facilityData(dict(facility_name='STR'))
        fac3 = facilityData(dict(facility_name='SCH'))
        fac1.save()
        fac2.save()
        fac3.save()
        us1 = userData(dict(
            name='test',
            password='test',
            type='admin',
            facility_id=fac1.id
        ))
        us1.save()

def clear_db():
    with app.app_context():
        db.drop_all()
    return "Database deleted please run flask migration"

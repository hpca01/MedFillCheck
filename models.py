from extensions import db
import datetime
import typing


# todo need to review the new structure - > user->facility->station->inventory
# todo barcode->user

class userData(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(123), nullable=False)
    # TODO need to add hash encyrption
    password = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(5), nullable=False)

    facility_id = db.Column(db.Integer, db.ForeignKey('facility.id'), nullable=True)
    auth_hash = db.Column(db.String, nullable=True)

    def __init__(self, data) -> None:
        self.name = data.get('name')
        self.password = data.get('password')
        self.type = data.get('type')
        self.facility_id = data.get('facility_id')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def verify_password(self, password):
        return password == self.password

    def _asdict(self):
        return dict(
            id=self.id,
            name=self.name,
            type=self.type,
            facility=facilityData.query.filter(facilityData.id == self.facility_id).first().__repr__()
        ), 201

class barcodeData(db.Model):
    __tablename__ = 'barcodes'

    '''
    intent of the barcode class is to share barcodes across platform
    '''

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    barcode = db.Column(db.String(128), nullable=False)
    medid = db.Column(db.String(128), nullable=False)

    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __init__(self, data):
        '''class constructor'''
        self.barcode = data.get('barcode')
        self.medid = data.get('medid')
        self.user = data.get('user')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def _asdict(self):
        return dict(
            barcode=self.barcode,
            medid=self.medid,
            user=self.user
        )

    def __repr__(self) -> str:
        return "Barcode: {} ||| MedID: {} ||| Submitted by: {}".format(self.barcode, self.medid, self.user)


class MedstationData(db.Model):
    __tablename__ = "medstation"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    station_name = db.Column(db.String(128), nullable=False)

    inventory_data = db.relationship('InventoryData', backref='medstation')
    facility_id = db.Column(db.Integer, db.ForeignKey('facility.id'), nullable=True)

    def __init__(self, data: typing.Dict['str', 'str']) -> None:
        self.station_name = data.get('station_name')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def _asdict(self):
        output = dict(
            station_name=self.station_name,
            devices=[device._asdict() for device in self.device_data]
        )


class InventoryData(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    med_description = db.Column(db.String(255), nullable=False)
    medid = db.Column(db.String(10), nullable=False)

    min = db.Column(db.Integer, nullable=False)
    max = db.Column(db.Integer, nullable=False)
    current = db.Column(db.Integer, nullable=False)
    pick_amount = db.Column(db.Integer, nullable=False)

    checked = db.Column(db.Boolean)
    entry_date = db.Column(db.DateTime())

    station_id = db.Column(db.Integer, db.ForeignKey('medstation.id'), nullable=True)

    def __init__(self, data) -> None:
        self.med_description = data.get('med_description')
        self.medid = data.get('medid')
        self.min = data.get('min')
        self.max = data.get('max')
        self.current = data.get('current')
        self.pick_amount = data.get('pick_amount')
        self.checked = False
        ##self.pulled_by to be added
        self.entry_date = datetime.datetime.now()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __asdict(self):
        dict_return = dict(
            med_description=self.med_description,
            medid=self.medid,
            min=self.min,
            max=self.max,
            current=self.current,
            pick_amount=self.pick_amount,
            checked=str(self.checked),
            entry_date=self.entry_date.__repr__(),
        )


class facilityData(db.Model):
    __tablename__ = 'facility'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    facility_name = db.Column(db.String(128), nullable=False)

    stations = db.relationship('MedstationData', backref='facility', lazy=True)
    users = db.relationship('userData', backref='facility', lazy=True)

    def __init__(self, data) -> None:
        '''class constructor'''
        self.facility_name = data.get('facility_name')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def _asdict(self):
        return dict(
            id=self.id,
            facility_name=self.facility_name,
            users=[user._asdict() for user in self.users]
        )

    def __repr__(self) -> str:
        return "{}".format(self.facility_name)




class BlackListToken(db.Model):
    __tablename__ = "blacklist"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String, nullable=True)

    def __init__(self, data: typing.Dict[str, str]):
        self.hash = data.get('hash')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def validate_blacklist(hash):
        blacklist = BlackListToken.query.filter(BlackListToken.hash == str(hash)).first()
        if blacklist is None:
            return True
        else:
            return False

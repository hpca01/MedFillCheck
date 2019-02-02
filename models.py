from extensions import db
import datetime
import typing


# todo need to review the new structure - > user->facility->station->inventory -- DONE
# todo barcode->user -- DONE

class userData(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(5), nullable=False)

    facility_id = db.Column(db.Integer, db.ForeignKey('facility.id'), nullable=True)
    auth_hash = db.Column(db.String, nullable=True)

    def __init__(self, *args, **kwargs) -> None:
        super(userData, self).__init__(*args, **kwargs)

    @property
    def facility(self)->str:
        facility = facilityData.query.filter(facilityData.id == self.facility_id).first()
        if facility is None:
            return "No Facility Found"
        else:
            return facility.facility_name

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
            facility_id=self.facility
        )


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

    inventory_data = db.relationship('InventoryData', backref='medstation', cascade="all, delete, delete-orphan")
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
        )
        return output

    def _refill_list_as_dict(self):
        #todo filter list by checked is false--DONE

        output = dict(
            station_name=self.station_name,
            refill_list=[refilldata._asdict_refill() for refilldata in self.inventory_data]
        )
        return output


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

    def _asdict_refill(self):
        if self.checked is not True:
            return self._asdict()


    def _asdict(self):
        dict_return = dict(
            med_description=self.med_description,
            medid=self.medid,
            min=self.min,
            max=self.max,
            current=self.current,
            pick_amount=self.pick_amount,
            checked=str(self.checked),
            entry_date=self.entry_date.isoformat(' ', 'seconds'),
        )
        return dict_return


class facilityData(db.Model):
    __tablename__ = 'facility'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    facility_name = db.Column(db.String(128), nullable=False)

    stations = db.relationship('MedstationData', backref='facility', lazy=True, cascade="all, delete, delete-orphan")
    users = db.relationship('userData', backref='facility', lazy=True, cascade="all, delete, delete-orphan")

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
            users=[user._asdict() for user in self.users],
            stations=[station._asdict() for station in self.stations]
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
        blacklist = BlackListToken.query.filter(BlackListToken.hash == hash).first()
        if blacklist is None:
            '''
            token isn't in blacklist
            '''
            return True
        else:
            '''
            token is in blacklist
            '''
            return False

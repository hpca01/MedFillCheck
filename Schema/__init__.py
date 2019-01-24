from extensions import ma
from marshmallow import fields


class RefillData(ma.Schema):
    med_description = fields.String()
    medid = fields.String()
    min=fields.Integer()
    max = fields.Integer()
    current = fields.Integer()
    pick_amount = fields.Integer()
    checked = fields.Boolean()
    entry_date = fields.LocalDateTime()


class RefillList(ma.Schema):
    station_name = fields.String(required=True)
    refills = fields.List(fields.Nested(RefillData), required=True)

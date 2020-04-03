from app import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

class Log(db.Model):
    __tablename__ = "t_log"
    id_trans = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    source = db.Column(db.String(100))
    destination = db.Column(db.String(100))
    fraud_type = db.Column(db.Integer)
    is_fraud = db.Column(db.Integer)

    def create(self):
      db.session.add(self)
      db.session.commit()
      return self
    def __init__(self,amount,date,time,source,destination,fraud_type,is_fraud):
        self.amount = amount
        self.date = date
        self.time = time
        self.source = source
        self.destination = destination
        self.fraud_type = fraud_type
        self.is_fraud = is_fraud
    def __repr__(self):
        return '' % self.id
db.create_all()
class LogSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Log
        sqla_session = db.session
    id_trans = fields.Integer(dump_only=True)
    amount = fields.Number(required=True)
    date = fields.Date(required=True)
    time = fields.Time(required=True)
    source = fields.String(required=True)
    destination = fields.String(required=True)
    body_email = fields.String(required=False)
    fraud_type = fields.String(required=True)
    is_fraud = fields.Integer(required=True)


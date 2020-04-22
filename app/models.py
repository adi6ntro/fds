from app import db, login
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime


class Log(db.Model):
    __tablename__ = "t_log"
    id = db.Column(db.Integer, primary_key=True)
    id_trans = db.Column(db.Integer)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    company_id = db.Column(db.String(250))
    source = db.Column(db.String(100))
    destination = db.Column(db.String(100))
    amount = db.Column(db.Integer)
    trans_type = db.Column(db.String(100))
    product_id = db.Column(db.String(250))
    ip_address = db.Column(db.String(100))
    ip_city = db.Column(db.String(100))
    ip_country = db.Column(db.String(100))
    longitude = db.Column(db.String(100))
    latitude = db.Column(db.String(100))
    geo_city = db.Column(db.String(100))
    geo_state = db.Column(db.String(100))
    geo_country = db.Column(db.String(100))
    fraud_type = db.Column(db.String(100))
    fraud_point = db.Column(db.Integer)
    fraud_cause = db.Column(db.Text)

    def create(self):
      db.session.add(self)
      db.session.commit()
      return self
    def __init__(self,id_trans,date,time,company_id,source,destination,amount,
        trans_type,product_id,ip_address,ip_city,ip_country,longitude,latitude,
        geo_city,geo_state,geo_country,fraud_type,fraud_point,fraud_cause):
        self.id_trans = id_trans
        self.date = date
        self.time = time
        self.company_id = company_id
        self.source = source
        self.destination = destination
        self.amount = amount
        self.trans_type = trans_type
        self.product_id = product_id
        self.ip_address = ip_address
        self.ip_city = ip_city
        self.ip_country = ip_country
        self.longitude = longitude
        self.latitude = latitude
        self.geo_city = geo_city
        self.geo_state = geo_state
        self.geo_country = geo_country
        self.fraud_type = fraud_type
        self.fraud_point = fraud_point
        self.fraud_cause = fraud_cause

    def __repr__(self):
        return '' % self.id_trans

class User(UserMixin, db.Model):
    __tablename__ = "t_user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def create(self):
      db.session.add(self)
      db.session.commit()
      return self
    # def __init__(self,username,email,password_hash):
    #     self.username = username
    #     self.email = email
    #     self.password_hash = password_hash
    def __repr__(self):
        return '<User {}>'.format(self.username)    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

db.create_all()

class LogSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Log
        sqla_session = db.session
    id = fields.Integer(dump_only=True)
    id_trans = fields.Integer(required=True)
    date = fields.Date(required=True)
    time = fields.Time(required=True)
    company_id = fields.String(required=True)
    source = fields.String(required=True)
    destination = fields.String(required=True)
    amount = fields.Number(required=True)
    trans_type = fields.String(required=True)
    product_id = fields.String(required=True)
    ip_address = fields.String(required=True)
    ip_city = fields.String(allow_none=True, missing=True)
    ip_country = fields.String(allow_none=True, missing=True)
    longitude = fields.String(required=True)
    latitude = fields.String(required=True)
    geo_city = fields.String(required=True)
    geo_state = fields.String(required=True)
    geo_country = fields.String(required=True)
    fraud_type = fields.String(required=True)
    fraud_point = fields.Integer(required=True)
    fraud_cause = fields.String(required=True)
    body_email = fields.String(required=False)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
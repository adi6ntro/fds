from app import db, login
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

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
    ip_address = db.Column(db.String(100))
    transaction_type = db.Column(db.String(100))

    def create(self):
      db.session.add(self)
      db.session.commit()
      return self
    def __init__(self,amount,date,time,source,destination,fraud_type,is_fraud,ip_address,transaction_type):
        self.amount = amount
        self.date = date
        self.time = time
        self.source = source
        self.destination = destination
        self.fraud_type = fraud_type
        self.is_fraud = is_fraud
        self.ip_address = ip_address
        self.transaction_type = transaction_type
    def __repr__(self):
        return '' % self.id

class User(UserMixin, db.Model):
    __tablename__ = "t_user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

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
    id_trans = fields.Integer(dump_only=True)
    amount = fields.Number(required=True)
    date = fields.Date(required=True)
    time = fields.Time(required=True)
    source = fields.String(required=True)
    destination = fields.String(required=True)
    body_email = fields.String(required=False)
    fraud_type = fields.String(required=True)
    is_fraud = fields.Integer(required=True)
    ip_address = fields.String(required=True)
    transaction_type = fields.String(required=True)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
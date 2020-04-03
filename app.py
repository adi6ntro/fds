from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from flask_mail import Mail, Message
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/dbfds'
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = 1
app.config['MAIL_USERNAME'] = 'report@indoalliz.com'
app.config['MAIL_PASSWORD'] = 'report#123'
app.config['MAIL_DEFAULT_SENDER'] = 'support@ottofds.id'
mail = Mail(app)

###Models####
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

@app.route('/logs', methods = ['GET'])
def index():
    get_logs = Log.query.all()
    log_schema = LogSchema(many=True)
    logs = log_schema.dump(get_logs)
    return make_response(jsonify({"log": logs}))
@app.route('/logs/<id>', methods = ['GET'])
def get_log_by_id(id):
    get_logs = Log.query.get(id)
    log_schema = LogSchema()
    logs = log_schema.dump(get_logs)
    return make_response(jsonify({"log": logs}))
@app.route('/logs', methods = ['POST'])
def create_product():
    data = request.get_json()
    log_schema = LogSchema()
    logs = log_schema.load(data)
    result = log_schema.dump(logs.create())
    if data["is_fraud"] == "1":
        msg = Message('Fraud Detection Warning', recipients=["aoi.soichiro@gmail.com"])
        # msg = Message('Fraud Detection Warning', recipients=["aoi.soichiro@gmail.com"],
        #         cc=["endang.fiansyah@@ottodigital.id"], bcc=["adi.guntoro@ottodigital.id"])
        msg.body = (data["body_email"])
        msg.html = (data["body_email"])
        mail.send(msg)
    return make_response(jsonify({"log": result}),200)
if __name__ == "__main__":
    app.run(debug=True)

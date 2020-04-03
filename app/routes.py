from flask import render_template, flash, redirect, url_for, request, jsonify, make_response
from app import app, mail
from app.models import Log, LogSchema
from flask_mail import Message
# from app.forms import LoginForm

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return "hello world!!!"
#     user = {'username': 'Adi Guntoro'}
#     posts = [
#         {
#             'author': {'username': 'Medio'},
#             'body': 'Beautiful day in Portland!'
#         },
#         {
#             'author': {'username': 'Jose'},
#             'body': 'The Avengers movie was so cool!'
#         }
#     ]
#     return render_template('index.html', title='Home', user=user, posts=posts)

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         flash('Login requested for user {}, remember_me={}'.format(
#             form.username.data, form.remember_me.data))
#         return redirect(url_for('index'))
#     return render_template('login.html',  title='Sign In', form=form)

@app.route('/logs', methods = ['GET'])
def get_log():
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

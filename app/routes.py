from flask import render_template, flash, redirect, url_for, request, jsonify, make_response
from app import app, mail, db
from app.models import Log, LogSchema, User
from flask_mail import Message
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
@app.route('/home')
@login_required
def index():
    get_logs = Log.query.order_by(Log.id_trans.desc()).all()
    return render_template('index.html', title='Home', logs=get_logs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/api/logs', methods = ['GET'])
def get_log():
    get_logs = Log.query.all()
    log_schema = LogSchema(many=True)
    logs = log_schema.dump(get_logs)
    return make_response(jsonify({"log": logs}))
@app.route('/api/logs/<id>', methods = ['GET'])
def get_log_by_id(id):
    get_logs = Log.query.get(id)
    log_schema = LogSchema()
    logs = log_schema.dump(get_logs)
    return make_response(jsonify({"log": logs}))
@app.route('/api/logs', methods = ['POST'])
def create_product():
    data = request.get_json()
    log_schema = LogSchema()
    logs = log_schema.load(data)
    result = log_schema.dump(logs.create())
    if data["is_fraud"] == "1":
        msg = Message('Fraud Detection Warning', recipients=["adi.guntoro@ottodigital.id"])
        # msg = Message('Fraud Detection Warning', recipients=["aoi.soichiro@gmail.com"],
        #         cc=["endang.fiansyah@@ottodigital.id"], bcc=["adi.guntoro@ottodigital.id"])
        msg.body = (data["body_email"])
        msg.html = (data["body_email"])
        mail.send(msg)
    return make_response(jsonify({"log": result}),200)

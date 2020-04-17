from flask import render_template, flash, redirect, url_for, request, jsonify, make_response, send_from_directory
from app import app, db
from app.models import Log, LogSchema, User
from flask_mail import Message
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_report_email
import os 

@app.route('/')
@app.route('/index')
@app.route('/home')
@login_required
def index():
    get_logs = Log.query.order_by(Log.id_trans.desc())
    page = request.args.get('page', 1, type=int)
    posts = get_logs.paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    return render_template('index.html', title='Home', logs=posts.items)

@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

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
def insert_log():
    data = request.get_json()
    log_schema = LogSchema()
    logs = log_schema.load(data)
    result = log_schema.dump(logs.create())
    if data["is_fraud"] == "1":
        subject = 'Fraud Detection Warning' 
        recipients=["adi.guntoro@ottodigital.id"]
        # msg = Message('Fraud Detection Warning', recipients=["aoi.soichiro@gmail.com"],
        #         cc=["endang.fiansyah@@ottodigital.id"], bcc=["adi.guntoro@ottodigital.id"])
        text_body = data["body_email"]
        html_body = data["body_email"]
        send_report_email(subject,recipients,text_body,html_body)
    return make_response(jsonify({"log": result}),200)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/search/logs', methods = ['POST'])
def search_log():
    get_logs = Log.query
    page = int(request.form['page']) if request.form['page'] else 1

    amount = request.form["amount"]
    search_amount = "%{}%".format(amount)
    date = request.form["date"]
    search_date = "%{}%".format(date)
    time = request.form["time"]
    search_time = "%{}%".format(time)
    source = request.form["source"]
    search_source = "%{}%".format(source)
    destination = request.form["destination"]
    search_destination = "%{}%".format(destination)
    is_fraud = request.form["is_fraud"]
    a = ['n', 'o', 't', 'N', 'O', 'T', ' ']
    fraud = 0 if any(x in is_fraud for x in a) else 1
    search_is_fraud = "%{}%".format(fraud)
    fraud_type = request.form["fraud_type"]
    search_fraud_type = "%{}%".format(fraud_type)
    ip_address = request.form["ip_address"]
    search_ip_address = "%{}%".format(ip_address)
    transaction_type = request.form["transaction_type"]
    search_transaction_type = "%{}%".format(transaction_type)

    if amount:
        get_logs = get_logs.filter(Log.amount.like(search_amount))
    if date:
        get_logs = get_logs.filter(Log.date.like(search_date))
    if time:
        get_logs = get_logs.filter(Log.time.like(search_time))
    if source:
        get_logs = get_logs.filter(Log.source.like(search_source))
    if destination:
        get_logs = get_logs.filter(Log.destination.like(search_destination))
    if is_fraud:
        get_logs = get_logs.filter(Log.is_fraud.like(search_is_fraud))
    if fraud_type:
        get_logs = get_logs.filter(Log.fraud_type.like(search_fraud_type))
    if ip_address:
        get_logs = get_logs.filter(Log.ip_address.like(search_ip_address))
    if transaction_type:
        get_logs = get_logs.filter(Log.transaction_type.like(search_transaction_type))
    
    get_logs = get_logs.order_by(Log.id_trans.desc())
    posts = get_logs.paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    tr_log = ''
    for row in posts.items:
        tr_row = '''<tr>
                        <td>{0}</td>
                        <td>{1}</td>
                        <td>{2}</td>
                        <td>{3}</td>
                        <td>{4}</td>
                        <td>{5}</td>
                        <td>{6}</td>
                        <td>{7}</td>
                        <td>{8}</td>
                        <td>{9}</td>
                    </tr>'''
        fraud = 'Fraud' if row.is_fraud == 1 else 'Not Fraud'
        tr_log = tr_log + tr_row.format(row.id_trans, row.amount, row.date, row.time, row.source,
                        row.destination, fraud, row.fraud_type, row.ip_address, row.transaction_type)

    next_page = posts.next_num if posts.has_next else '#'
    if next_page != '#':
        str_next_url = '<a onclick="search_log(\''+str(next_page)+'\')">'
    else:
        str_next_url = '''<a>'''
    str_next_url = str_next_url + '''Older <span aria-hidden="true">&rarr;</span></a>'''

    prev_page = posts.prev_num if posts.has_prev else '#'
    if prev_page != '#':
        str_prev_url = '<a onclick="search_log(\''+str(prev_page)+'\')">'
    else:
        str_prev_url = '''<a>'''
    str_prev_url = str_prev_url + '''<span aria-hidden="true">&larr;</span> Newer</a>'''

    return jsonify({'str_next_url': str_next_url, 'str_prev_url': str_prev_url,
                    'next_page': next_page, 'prev_page': prev_page, 'tr_log': tr_log})

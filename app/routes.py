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
from bs4 import BeautifulSoup
import geoip2.database
from geoip2.errors import AddressNotFoundError
from geopy.geocoders import Nominatim
from sqlalchemy import func

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
        if user.is_active == 0:
            flash('Username is not active')
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
        user = User(username=form.username.data, email=form.email.data, fullname=form.fullname.data, is_active=0)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered. Please contact the administrator to activate your account!')
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
    log_schema = LogSchema()
    data = request.get_json()

    soup = BeautifulSoup(data["body_email"],'html.parser')
    title = soup.findAll('span',{"id" : "title"})
    for link in title:
        data['fraud_type'] = "POTENTIAL FRAUD" \
            if "POTENTIAL" in link.findAll(text=True)[0] else "FRAUD"
    cause = soup.findAll('span',{"id" : "cause"})
    data['fraud_cause'] = ''
    for link in cause:
        data['fraud_cause'] = data['fraud_cause'] + link.findAll(text=True)[0] + '<br>'
    point = soup.findAll('span',{"id" : "point"})
    for link in point:
        data['fraud_point'] = link.findAll(text=True)[0]

    #geolocation
    geolocator = Nominatim(user_agent="fds-v1")
    location = geolocator.reverse("%s, %s"%(data['longitude'],data['latitude']))
    address = location.raw['address']
    data['geo_city'] = address.get('city', '')
    data['geo_state'] = address.get('state', '')
    data['geo_country'] = address.get('country', '')
    
    #ip location
    reader = geoip2.database.Reader('GeoLite2-City.mmdb')
    try:
        response = reader.city(data['ip_address'])
        data['ip_city'] = response.city.name
        data['ip_country'] = response.country.name
    except AddressNotFoundError:
        data['ip_city'] = None
        data['ip_country'] = None

    logs = log_schema.load(data)
    result = log_schema.dump(logs.create())
    if result:
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

@app.route('/log/<id>/popup')
@login_required
def user_popup(id):
    log = Log.query.filter_by(id=id).first_or_404()
    return render_template('log_popup.html', log=log)


@app.route('/search/logs', methods = ['POST'])
def search_log():
    get_logs = Log.query
    page = int(request.form['page']) if request.form['page'] else 1

    id_trans = request.form["id_trans"]
    search_id_trans = "%{}%".format(id_trans)
    date_time = request.form["date_time"]
    search_date_time = "%{}%".format(date_time)
    company_id = request.form["company_id"]
    search_company_id = "%{}%".format(company_id)
    source = request.form["source"]
    search_source = "%{}%".format(source)
    destination = request.form["destination"]
    search_destination = "%{}%".format(destination)
    amount = request.form["amount"]
    search_amount = "%{}%".format(amount)
    trans_type = request.form["trans_type"]
    search_trans_type = "%{}%".format(trans_type)
    product_id = request.form["product_id"]
    search_product_id = "%{}%".format(product_id)
    ip_address = request.form["ip_address"]
    search_ip_address = "%{}%".format(ip_address)
    ip_location = request.form["ip_location"]
    search_ip_location = "%{}%".format(ip_location)
    longlat = request.form["longlat"]
    search_longlat = "%{}%".format(longlat)
    geo_location = request.form["geo_location"]
    search_geo_location = "%{}%".format(geo_location)
    fraud_type = request.form["fraud_type"]
    search_fraud_type = "%{}%".format(fraud_type)
    fraud_point = request.form["fraud_point"]
    search_fraud_point = "%{}%".format(fraud_point)

    if id_trans:
        get_logs = get_logs.filter(Log.id_trans.like(search_id_trans))
    if date_time:
        get_logs = get_logs.filter(func.concat(Log.date, ' ', Log.time).like(search_date_time))
    if company_id:
        get_logs = get_logs.filter(Log.company_id.like(search_company_id))
    if source:
        get_logs = get_logs.filter(Log.source.like(search_source))
    if destination:
        get_logs = get_logs.filter(Log.destination.like(search_destination))
    if amount:
        get_logs = get_logs.filter(Log.amount.like(search_amount))
    if trans_type:
        get_logs = get_logs.filter(Log.trans_type.like(search_trans_type))
    if product_id:
        get_logs = get_logs.filter(Log.product_id.like(search_product_id))
    if ip_address:
        get_logs = get_logs.filter(Log.ip_address.like(search_ip_address))
    if ip_location:
        get_logs = get_logs.filter(func.concat(Log.ip_city, ', ', Log.ip_country).like(search_ip_location))
    if longlat:
        get_logs = get_logs.filter(func.concat(Log.longitude, ', ', Log.latitude).like(search_longlat))
    if geo_location:
        get_logs = get_logs.filter(func.concat(Log.geo_city, ', ', Log.geo_state, ', ', Log.geo_country).like(search_geo_location))
    if fraud_type:
        get_logs = get_logs.filter(Log.fraud_type.like(search_fraud_type))
    if fraud_point:
        get_logs = get_logs.filter(Log.fraud_point.like(search_fraud_point))
    
    get_logs = get_logs.order_by(Log.id.desc())
    posts = get_logs.paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    tr_log = ''
    for row in posts.items:
        tr_row = '''<tr><td class="log_popup2" style="cursor: pointer;">
                    <a class="btn btn-default" href="#" data-toggle="tooltip" title="Lihat Detail">
                    <span class="glyphicon glyphicon-search"></span></a>
                    <span style="display: none;">{0}</span></td><td>{1}</td>
                    <td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>Rp {6}</td>
                    <td>{7}</td><td>{8}</td><td>{9}</td><td>{10}</td><td>{11}</td>
                    <td>{12}</td><td>{13}</td><td>{14}</td><td class="log_popup3" style="cursor: pointer;">
                    <a class="btn btn-default" href="#" data-toggle="tooltip" title="Lihat Detail">
                    <span class="glyphicon glyphicon-search"></span></a>
                    <span style="display: none;">{15}</span></td></tr>'''

        date_time = str(row.date) + ' ' + str(row.time)
        ip_location = str(row.ip_city) + ', ' + str(row.ip_country)
        longlat = str(row.longitude) + ', ' + str(row.latitude)
        geo_location = str(row.geo_city) + ', ' + str(row.geo_state) + ', ' + str(row.geo_country)

        tr_log = tr_log + tr_row.format(row.id, row.id_trans, date_time, row.company_id, row.source,
                    row.destination, ("{:,}".format(int(row.amount)).replace(',', '.')), row.trans_type, row.product_id, row.ip_address,
                    ip_location, longlat, geo_location, row.fraud_type, row.fraud_point, row.id)

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

from json import dump, dumps, load
from logging import FileHandler, basicConfig, error, DEBUG, debug
from os import getenv, getcwd
from subprocess import Popen
import requests 
import xml.etree.ElementTree as ET 
from flask import Flask, request, send_file, render_template
import ast
import xmltodict
from siebel import Siebel, Change_log_action
import time
from datetime import timedelta
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUserMixin,
                            confirm_login, fresh_login_required)

app = Flask(__name__)

class User(UserMixin):
    def __init__(self, name, id, ip, active=True, ldap_authenticated = False, last_activity=0):
        self.name = name
        self.id = id
        self.ip = ip
        self.active = active
        self.ldap_authenticated = ldap_authenticated
        self.last_activity = last_activity

    def is_active(self):
        # Here you should write whatever the code is
        # that checks the database if your user is active
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True


class Anonymous(AnonymousUserMixin):
    name = u"Anonymous"


USERS = {}
USER_NAMES = [{user.name: user} for user in USERS]
user_id_count = 0
# USER_NAMES = dict((u.name, u) for u in USERS.itervalues())
SECRET_KEY = "secretkey"
app.config.from_object(__name__)

login_manager = LoginManager()

login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"
login_manager.needs_refresh_message = (u"Session timedout, please re-login")
login_manager.needs_refresh_message_category = "info"


def getXml(username, password):
    return f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wss="http://wsserver">
    <soapenv:Header/>
    <soapenv:Body>
    <wss:checkAuthentication>
        <wss:wsUserId>LDMLDAP</wss:wsUserId>
        <wss:wsPassword>ldmvdfldap</wss:wsPassword>
        <wss:userName>{username}</wss:userName>
        <wss:password>{password}</wss:password>
        <wss:domainName>nsi</wss:domainName>
    </wss:checkAuthentication>
    </soapenv:Body>
    </soapenv:Envelope>'''


def isLdapAuthenticated(xml_str):
    data_json = ast.literal_eval(dumps(xmltodict.parse(xml_str)))
    return "LDAP Account : OK" == data_json["soapenv:Envelope"]["soapenv:Body"]["checkAuthenticationResponse"]["checkAuthenticationReturn"]["ldapResults"]["ldapResults"]["description"]


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)


@login_manager.user_loader
def load_user(ip):
    for username, user in USERS.items():
        if user.ip == ip:
            return USERS.get(username)


login_manager.setup_app(app)


@app.route("/")
def home():
    return redirect(url_for("request_log_page"))


@app.route("/request_log_page", methods=["GET", "POST"])
# @login_required
def request_log_page():
    if load_user(request.remote_addr) and load_user(request.remote_addr).ldap_authenticated:
        print("authenticated. (on request_log_page")
        return render_template("index.html")
    else:
        return redirect(url_for("login"))


@login_manager.unauthorized_handler
@app.route("/login", methods=["GET", "POST"])
def login():
    global user_id_count
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        remember = request.form.get("remember-me") == "on"
        username = request.form["username"]
        data = getXml(username, request.form["password"])
        r = requests.post(url=getenv("LDAP_URL"), data=data, headers={'Content-Type': 'application/xml', 'SOAPAction': ''})
        if isLdapAuthenticated(r.text):
            user_id_count += 1
            current_user = User(name=username,
                                id=user_id_count,
                                ip=request.remote_addr,
                                active=True,
                                ldap_authenticated=True,
                                last_activity=time.time())
            USERS.update({username:  current_user})
            USERS[username].ldap_authenticated = True
            login_user(USERS[username], remember=remember)
            # return render_template("index.html")
            return redirect(url_for("request_log_page"))
        else:
            flash("Invalid credentials.")
            return render_template("login.html", status_message="Invalid credentials.")
            #TODO: add invalid cred. message along with render_template


@app.route("/reauth", methods=["GET", "POST"])
@login_required
def reauth():
    if request.method == "POST":
        confirm_login()
        flash(u"Reauthenticated.")
        return redirect(request.args.get("next") or url_for("index"))
    return render_template("reauth.html")


@app.route("/logout")
@login_required
def logout():
    
    logout_user()
    flash("Logged out.")
    return redirect(url_for("index"))


@app.route("/open_log", methods=["POST"])
def open_log():
    try:
        req_data = request.form if len(request.form) != 0 else request.json
        debug(req_data)
        siebel = Siebel(req_data)
        response = siebel.change_log_level(Change_log_action.INCREASE)
        debug(response)
        response_message = response["response_message"]
        response_status = response["status"]
    except:
        error("Error occurred:", exc_info=True)
        response_message = {"response_message": "Something went wrong."}
        response_status = 404
    return app.response_class(
        response=dumps(response_message),
        status=response_status,
        mimetype='application/json'
    )


@app.route("/close_log", methods=["POST"])
def close_log():
    try:
        req_data = request.form if len(request.form) != 0 else request.json
        debug(req_data)
        siebel = Siebel(req_data)
        response = siebel.change_log_level(Change_log_action.DECREASE)
        debug(response)
        response_message = response["response_message"]
        response_status = response["status"]
    except:
        error("Error occurred:", exc_info=True)
        response_message = {"response_message": "Something went wrong."}
        response_status = 404
    return app.response_class(
        response=dumps(response_message),
        status=response_status,
        mimetype='application/json'
    )


@app.route("/request_log", methods=["POST"])
def request_log():
    req_data = request.form if len(request.form) != 0 else request.json
    debug(req_data)
    siebel = Siebel(req_data)
    file_name = siebel.request_log()
    debug(file_name)
    if type(file_name) == str:
        return send_file(file_name, mimetype="application/x-zip-compressed", as_attachment=True)
    else:
        return app.response_class(
            response=dumps(file_name["response_message"]),
            status=file_name["status"],
            mimetype='application/json'
        )


@app.route("/update_servers", methods=["POST"])
def update_servers():
    req_data = request.form if len(request.form) != 0 else request.json
    debug(req_data)
    machine_no = req_data.get("machine_no")
    log_level_last_updated = req_data.get("log_level_last_updated")
    log_level_status = req_data.get("log_level_status")
    with open("static/data/servers.json") as f:
        data = load(f)
    with open("static/data/servers.json", "w+") as f:
        data[int(machine_no) - 1].update({"log_level_status": log_level_status})
        data[int(machine_no) - 1].update({"log_level_last_updated": log_level_last_updated})
        data[int(machine_no) - 1].update({"last_user_name": load_user(request.remote_addr).name})
        dump(data, f)
    debug(f"servers.json has been updated on machine no# {machine_no}.")
    return app.response_class(
        response=dumps({"response_message": "Success!"}),
        status=200,
        mimetype='application/json'
    )


@app.route("/get_servers", methods=["GET"])
def get_servers():
    with open("static/data/servers.json") as f:
        data = load(f)
    debug(f"servers.json has been retrieved.")
    return app.response_class(
        response=dumps(data),
        status=200,
        mimetype='application/json'
    )


if __name__ == "__main__":
    basicConfig(handlers=[FileHandler(encoding='utf-8', filename='server.log', mode='w')],
                level=DEBUG,
                format=u'%(levelname)s - %(name)s - %(asctime)s: %(message)s')
    Popen("python log_status.py", cwd=getcwd(), shell=True)
    app.run(host=getenv("host_address"), port=getenv("host_port"), debug=False)

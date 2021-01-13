from json import dumps
from logging import FileHandler, basicConfig, error, DEBUG, debug
from os import getenv, getcwd
from subprocess import Popen

from flask import Flask, request, send_file, render_template

from siebel import Siebel, Change_log_action

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("index.html")


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


if __name__ == "__main__":
    basicConfig(handlers=[FileHandler(encoding='utf-8', filename='server.log', mode='w')],
                level=DEBUG,
                format=u'%(levelname)s - %(name)s - %(asctime)s: %(message)s')
    Popen("python log_status.py", cwd=getcwd(), shell=True)
    app.run(host=getenv("host_address"), port=5005, debug=False)
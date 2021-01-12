from json import dumps
from logging import error
from os import getenv

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
        print(req_data)
        siebel = Siebel(req_data)
        siebel.change_log_level(Change_log_action.INCREASE)
        response_message = "Log level increased."
        response_status = 200
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
        print("@@ REQ_DATA:\n\n")
        print(req_data)
        siebel = Siebel(req_data)
        siebel.change_log_level(Change_log_action.DECREASE)
        response_message = "Log level decreased."
        response_status = 200
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
    siebel = Siebel(req_data)
    return send_file(siebel.request_log(), mimetype="application/x-zip-compressed", as_attachment=True)


if __name__ == "__main__":
    app.run(host=getenv("host_address"), port=5005, debug=False)
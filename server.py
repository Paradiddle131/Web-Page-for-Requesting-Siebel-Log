from flask import Flask, request, send_file, render_template
from json import dump, dumps, load
import subprocess
from dotenv import load_dotenv
from os import getenv, system, getcwd, path
import time
from glob import glob
from pprint import pprint

app = Flask(__name__)
args = None
path_project = getcwd()
path_batch = path.join(path_project, "plink_.bat")
response, servers = [{} for _ in range(2)]
open_machines = []
isTest = False

def setup():
	global args, servers
	load_dotenv('config.env')
	args = {"serv_ip": getenv('serv_ip'),
			"servpw": getenv('servpw'),
			"path_log": getenv('path_log'),
			"path_unix_log": getenv('path_unix_log'),
			"winscp_hostkey": getenv('winscp_hostkey')
	}
	with open("servers.json", "r") as f:
		servers = load(f)

		
@app.route("/")
def hello():
    return render_template("index.html")
	
		
@app.route("/records")
def records():
    return render_template("records.html")
	
	
def run_batch(args):
	system(fr'C:\Windows\System32\cmd.exe /c {path_batch} "{args["serv_ip"]}" "{args["servpw"]}" "{args["path_log"]}" "{args["path_unix_log"]}" "{args["winscp_hostkey"]}" "{args["Action"]}" "{args["keyword"]}" "{args["machine_no"]}" "{args["server_name"]}" "{args["time_log"]}" "{args["component"]}"')
	#subprocess.Popen(["plink_.bat", args["serv_ip"], args["servpw"], args["path_log"], args["path_unix_log"], args['Action'], args['keyword'], args['machine_no'], args["time_log"], args["component"]], shell=True)


def get_request_attribute(req_data, attribute_name):
	return servers[int(req_data.get('machine_no'))-1][attribute_name]


@app.route("/request_log", methods=["POST"])
def request_log():
	try:
		req_data = request.form
		if req_data.get('Action') is None:
			with open("static/data/active_servers.json") as d:
				data = load(d)
			with open("static/data/active_servers.json", "w+") as f:
				current_data = {
					"Email": req_data.get("Email"),
					"Machine": req_data.get("Machine"),
					"Date_activated": req_data.get("Date_activated"),
					"Status": req_data.get("Status")
				}
				data.append(current_data)
				dump(data, f)
			return app.response_class(
			    response=dumps("Success!"),
			    status=200,
			    mimetype='application/json'
			)	
		isTest = True if 'isTest' in req_data else False
		if not isTest:
			args.update({"serv_ip": get_request_attribute(req_data, 'IP'),
						 "server_name": "SBL_ADM01"})
		else:
			args.update({"server_name": "SBL_ADM01"})
		time_log = str(time.time())
		args.update({"Action": req_data.get('Action'),
					"keyword": req_data.get('keyword'),
					"machine_no": req_data.get('machine_no'),
					"time_log": time_log,
					"component": get_request_attribute(req_data, 'Component_name')})
		run_batch(args)
		if req_data.get('Action') == "REQUEST_LOG":
			print("SENDING FILE...")
			return send_file(glob(f"{getenv('path_file_to_upload')}\{time_log}*.zip")[-1], attachment_filename="your_log.zip")
		elif req_data.get('Action') == "OPEN_LOG":
			open_machines.append(servers[int(req_data.get("machine_no"))-1]['hostname'])
			response_status = 201
			response.update({"response_message": "Log level increased.",
							"open_machines": open_machines})
		elif req_data.get('Action') == "CLOSE_LOG":
			open_machines.remove(servers[int(req_data.get("machine_no"))-1]['hostname'])
			response_status = 202
			response.update({"response_message": "Log level decreased.",
							"open_machines": open_machines})
		return app.response_class(
			response=dumps(response),
			status=response_status,
			mimetype='application/json'
		)
	except Exception as e:
		print("ERROR OCCURRED:\n\n")
		print(e)
		return app.response_class(
		    response=dumps("Something wrong!"),
		    status=404,
		    mimetype='application/json'
		)


if __name__ == "__main__":
	setup()
	app.run(host="172.24.84.34", port=5004, debug=False)
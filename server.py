from flask import Flask, request, send_file, render_template
from json import dump, dumps, load
import subprocess
from dotenv import load_dotenv
from os import getenv, system, getcwd, path
import time
from glob import glob
from pprint import pprint
from logging import error

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
			"path_unix_log": getenv('path_unix_log_ADM'),
			"winscp_hostkey": getenv('winscp_hostkey')
	}
	with open("static/data/servers.json", "r") as f:
		servers = load(f)

		
@app.route("/")
def hello():
    return render_template("index.html")
	
		
@app.route("/records")
def records():
    return render_template("records.html")
	
	
def run_batch(args):
	system(fr'C:\Windows\System32\cmd.exe /c {path_batch} "{args["serv_ip"]}" "{args["servpw"]}" "{args["path_log"]}" "{args["path_unix_log"]}" "{args["winscp_hostkey"]}" "{args["Server_action"]}" "{args["keyword"]}" "{args["machine_no"]}" "{args["server_name"]}" "{args["time_log"]}" "{args["component"]}"')
	#subprocess.Popen(["plink_.bat", args["serv_ip"], args["servpw"], args["path_log"], args["path_unix_log"], args['Server_action'], args['keyword'], args['machine_no'], args["time_log"], args["component"]], shell=True)


def get_request_attribute(req_data, attribute_name):
	return servers[int(req_data.get('machine_no'))-1][attribute_name]


@app.route("/request_log", methods=["POST"])
def request_log():
	try:
		req_data = request.form if len(request.form) != 0 else request.json
		print(req_data)
		if req_data.get('Server_action') == "LOG_USER_ACTIVITY":
			with open("static/data/user_activity.json") as d:
				try:
					data = load(d)
				except:
					print("No data found.")
					data = []
			current_data = {
				"Email": req_data.get("Email"),
				"Machine": req_data.get("Machine"),
				"Date_activated": req_data.get("Date_activated"),
				"User_action": req_data.get("User_action")
			}
			data.append(current_data)
			with open("static/data/user_activity.json", "w+") as f:
				dump(data, f)
			print("user_activity.json has been updated.")
			return app.response_class(
			    response=dumps("Success!"),
			    status=200,
			    mimetype='application/json'
			)				
		elif req_data.get('Status') is not None:
			with open("static/data/active_servers.json") as d:
				try:
					data = load(d)
				except:
					print("No data found.")
					data = []
			data[req_data.get("Machine")]["Email"] = req_data.get("Email")
			data[req_data.get("Machine")]["Date_activated"] = req_data.get("Date_activated")
			data[req_data.get("Machine")]["Status"] = req_data.get("Status")
			with open("static/data/active_servers.json", "w+") as f:
				dump(data, f)
			print("active_servers.json has been updated.")
			return app.response_class(
			    response=dumps("Success!"),
			    status=200,
			    mimetype='application/json'
			)	
		isTest = True if 'isTest' in req_data else False
		if not isTest:
			pass
			args.update({"serv_ip": get_request_attribute(req_data, 'IP'),
						 "servpw": get_request_attribute(req_data, 'Password'),
						 "winscp_hostkey": get_request_attribute(req_data, 'hostkey'),
						 "server_name": get_request_attribute(req_data, 'server_name'),
						 "path_unix_log": getenv('path_unix_log')})
		else:
			args.update({"server_name": "SBL_ADM01"})
		time_log = str(time.time())
		args.update({"Server_action": req_data.get('Server_action'),
					"keyword": req_data.get('keyword'),
					"machine_no": req_data.get('machine_no'),
					"time_log": time_log,
					"component": get_request_attribute(req_data, 'Component_name')})
		run_batch(args)
		if req_data.get('Server_action') == "REQUEST_LOG":
			print("SENDING FILE...")
			return send_file(glob(f"{getenv('path_file_to_upload')}\{time_log}*.zip")[-1], attachment_filename="your_log.zip")
		elif req_data.get('Server_action') == "OPEN_LOG":
			try:
				open_machines.append(servers[int(req_data.get("machine_no"))-1]['hostname'])
			except:
				print(servers[int(req_data.get("machine_no"))-1]['hostname'] + " is not open.")
			response_status = 201
			response.update({"response_message": "Log level increased.",
							"open_machines": open_machines})
		elif req_data.get('Server_action') == "CLOSE_LOG":
			try:
				open_machines.remove(servers[int(req_data.get("machine_no"))-1]['hostname'])
			except:
				print(servers[int(req_data.get("machine_no"))-1]['hostname'] + " is not open.")
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
		error(e, exc_info=True)
		return app.response_class(
		    response=dumps("Something wrong!"),
		    status=404,
		    mimetype='application/json'
		)


if __name__ == "__main__":
	setup()
	app.run(host="172.24.84.34", port=5004, debug=False)
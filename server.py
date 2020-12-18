from flask import Flask, request, send_file, render_template
from json import dumps
import subprocess
from dotenv import load_dotenv
from os import getenv, system, getcwd, path
import time
from glob import glob

app = Flask(__name__)
args = None
path_project = getcwd()
path_batch = path.join(path_project, "plink_.bat")

def setup():
	global args
	load_dotenv('config.env')
	args = {"serv_ip": getenv('serv_ip'),
			"servpw": getenv('servpw'),
			"path_log": getenv('path_log'),
			"path_unix_log": getenv('path_unix_log'),
			"winscp_hostkey": getenv('winscp_hostkey')
	}

		
@app.route("/")
def hello():
    return render_template("index.html")
	
	
def run_batch(args):
	system(fr'C:\Windows\System32\cmd.exe /c {path_batch} "{args["serv_ip"]}" "{args["servpw"]}" "{args["path_log"]}" "{args["path_unix_log"]}" "{args["winscp_hostkey"]}" "{args["Action"]}" "{args["keyword"]}" "{args["machine_no"]}" "{args["server_name"]}" "{args["time_log"]}" "{args["component"]}"')
	#subprocess.Popen(["plink_.bat", args["serv_ip"], args["servpw"], args["path_log"], args["path_unix_log"], args['Action'], args['keyword'], args['machine_no'], args["time_log"], args["component"]], shell=True)


@app.route("/request_log", methods=["POST"])
def request_log():
	try:
		req_data = request.form
		if req_data.get('Action') is None:
			print("Form data is missing.")
			exit()
		time_log = str(time.time())
		args.update({"Action": req_data.get('Action'),
					"keyword": req_data.get('keyword'),
					"machine_no": req_data.get('machine_no'),
					"server_name": req_data.get('server_name'),
					"time_log": time_log,
					"component": req_data.get('name_component')})
		run_batch(args)
		if req_data.get('Action') == "REQUEST_LOG":
			return send_file(glob(f"{getenv('path_file_to_upload')}\{time_log}*.log")[-1], attachment_filename="your_log.log")
		else:
			response_message = "Log level increased." if req_data.get('Action') == "OPEN_LOG" else "Log level decreased."
			response_status = 201 if req_data.get('Action') == "OPEN_LOG" else 202
			return app.response_class(
				response=dumps(response_message),
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
	app.run(host=getenv("host_address"), port=5003, debug=False)
from flask import Flask, request, send_file, render_template
from json import dump, dumps, load
import subprocess
from dotenv import load_dotenv
from os import getenv, system, getcwd, path, chdir
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
    
    
def batch_find_file():
    batcmd = f'''plink -hostkey "{args["winscp_hostkey"]}" -batch siebel@{args["serv_ip"]} -pw {args["servpw"]} "cd {args["path_unix_log"]};echo $(grep -l {args["keyword"]} *.log);"'''
    return subprocess.check_output(batcmd, shell=True, text=True).split()


def batch_request_log(files):
    files_str = ""
    for _file in files:
        batcmd = f'''"C:\\Program Files (x86)\\WinSCP\\WinSCP.exe" /command "option batch on" "option confirm off" "open -hostkey=""{args["winscp_hostkey"]}"" siebel:"{args["servpw"]}"@"{args["serv_ip"]}"" "get {args["path_unix_log"]}/{_file} E:\\LogCopyAutomation\\{_file}" "/log={args["path_log"]}\\LogCopy_{_file}"'''
        print("@@ WINSCP OUTPUT @@\n\n")
        subprocess.check_output(batcmd, shell=True, text=True)
        files_str += _file + " "
    batcmd = f'''"C:\\Program Files\\7-Zip\\7z.exe" a {args["keyword"]}.zip {files_str}-mx5'''
    print("@@ 7z OUTPUT @@\n\n")
    chdir("E:\\LogCopyAutomation")
    subprocess.check_output(batcmd, shell=True, text=True)
    for _file in files:
        subprocess.check_output(f"del {_file}", shell=True, text=True)
    chdir(path_project)
    

def batch_change_log_level(action):
    '''action: "increase" or "decrease" '''
    if action != "increase" and action != "decrease":
        print("Wrong argument passed:", action)
        return None
    batcmd = f'''plink -hostkey "{args["winscp_hostkey"]}" -batch siebel@{args["serv_ip"]} -pw {args["servpw"]} "cd {getenv("path_scripts")};./log_{action}.sh {args["server_name"]} {args["component"]};"'''
    print("@@ LOG CHANGE LEVEL COMMAND @@\n\n")
    print(batcmd)
    output = subprocess.check_output(batcmd, shell=True, text=True)
    print("@@ LOG CHANGE LEVEL OUTPUT @@\n\n")
    print(output)
    # assert not output
    return output


def get_request_attribute(req_data, attribute_name):
    return servers[int(req_data.get('machine_no'))-1][attribute_name]


@app.route("/request_log", methods=["POST"])
def request_log():
    response_status = 200
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
                status=response_status,
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
                status=response_status,
                mimetype='application/json'
            )    
        isTest = True if 'isTest' in req_data else False
        if not isTest:
            pass
            args.update({"serv_ip": get_request_attribute(req_data, 'IP'),
                         "servpw": get_request_attribute(req_data, 'Password'),
                         "winscp_hostkey": get_request_attribute(req_data, 'hostkey'),
                         "server_name": get_request_attribute(req_data, 'server_name'),
                         "path_unix_log": getenv('path_unix_log'),
                         "component_name": get_request_attribute(req_data, 'component_name'),
                         "component": get_request_attribute(req_data, 'component')},
                         )
        else:
            args.update({"server_name": "SBL_ADM01"})
        time_log = str(time.time())
        args.update({"Server_action": req_data.get('Server_action'),
                    "keyword": req_data.get('keyword'),
                    "machine_no": req_data.get('machine_no'),
                    "time_log": time_log,
                    "component_name": get_request_attribute(req_data, 'component_name'),
                    "component": get_request_attribute(req_data, 'component')})
        if req_data.get('Server_action') == "REQUEST_LOG":
            batch_change_log_level("decrease")
            files = batch_find_file()
            assert files, "Couldn't find any files."
            #TODO: method: return 404 
            batch_request_log(files)
            print("SENDING FILE...")
            return send_file(glob(path.join(getenv('path_file_to_upload'), req_data.get('keyword')+".zip"))[-1], attachment_filename="your_log.zip")
        else:
            action = "increase" if req_data.get('Server_action') == "OPEN_LOG" else "decrease"
            try:
                batch_change_log_level(action)
                if action == "increase":
                    open_machines.append(servers[int(req_data.get("machine_no"))-1]['hostname'])
                else:
                    try:
                        open_machines.remove(servers[int(req_data.get("machine_no"))-1]['hostname'])
                    except ValueError as e:
                        error(servers[int(req_data.get("machine_no"))-1]['hostname'] + " is not open.", exc_info=True)
            except Exception as e:
                error(e, exc_info=True)
            response.update({"response_message": f"Log level {action}d.",
            "open_machines": open_machines})
        return app.response_class(
            response=dumps(response),
            status=response_status,
            mimetype='application/json'
        )
    except Exception as e:
        error("ERROR OCCURRED:\n\n", exc_info=True)
        return app.response_class(
            response=dumps("Something wrong!"),
            status=404,
            mimetype='application/json'
        )


if __name__ == "__main__":
    setup()
    app.run(host=getenv("host_address"), port=5005, debug=False)
import subprocess
from glob import glob
from json import load
from os import getenv, getcwd, path, chdir

from dotenv import load_dotenv

path_project = getcwd()
path_batch = path.join(path_project, "plink_.bat")
response = {}
open_machines = []
isTest = False


def find_file(args):
    batcmd = f'''plink -hostkey "{args["winscp_hostkey"]}" -batch siebel@{args["serv_ip"]} -pw {args["servpw"]} "cd {args["path_unix_log"]};echo $(grep -l {args["keyword"]} *.log);"'''
    return subprocess.check_output(batcmd, shell=True, text=True).split()


class Response_type:
    LOG_LEVEL_INCREASED = "LOG_LEVEL_INCREASED"
    LOG_LEVEL_DECREASED = "LOG_LEVEL_DECREASED"
    FILE = "FILE"

class Change_log_action:
    INCREASE = "increase"
    DECREASE = "decrease"

class Siebel:
    load_dotenv("config.env")
    def __init__(self, req_data, isADM):
        self.isADM = isADM
        self.req_data = req_data
        with open("static/data/servers.json", "r") as f:
            self.servers = load(f)
        self.response = {"type": Response_type,
                         "response": {"response_message": ""},
                         "status": 0,
                         "mimetype": ""}
        if self.isADM:
            self.args = {
                "serv_ip": getenv("serv_ip"),
                "servpw": getenv("servpw"),
                "path_unix_log": getenv("path_unix_log_ADM"),
                "winscp_hostkey": getenv("winscp_hostkey"),
                "server_name": "SBL_ADM01"
            }
        else:
            self.args = {
                "serv_ip": self.get_request_attribute("IP"),
                "servpw": self.get_request_attribute("Password"),
                "winscp_hostkey": self.get_request_attribute("hostkey"),
                "server_name": self.get_request_attribute("server_name"),
                "path_unix_log": getenv("path_unix_log"),
                "component_name": self.get_request_attribute("component_name"),
                "component": self.get_request_attribute("component"),
            }
        self.args.update(
            {
                "path_log": getenv("path_log"),
                "Server_action": self.req_data.get("Server_action"),
                "keyword": self.req_data.get("keyword"),
                "machine_no": self.req_data.get("machine_no"),
                "component_name": self.get_request_attribute("component_name"),
                "component": self.get_request_attribute("component"),
            }
        )


    def get_request_attribute(self, attribute_name):
        return self.servers[int(self.req_data.get("machine_no")) - 1][attribute_name]


    def change_log_level(self, action):
        """action: type:Change_log_action, "INCREASE" or "DECREASE" """
        if action != Change_log_action.INCREASE and action != Change_log_action.DECREASE:
            print("Wrong argument passed:", action)
            return None
        if self.isADM:
            batcmd = f'''plink -batch siebel@{self.args["serv_ip"]} -pw {self.args["servpw"]} "cd {getenv("path_scripts")};./log_{action}.sh {self.args["server_name"]} {self.args["component"]};"'''
        else:
            batcmd = f'''plink -hostkey "{self.args["winscp_hostkey"]}" -batch siebel@{self.args["serv_ip"]} -pw {self.args["servpw"]} "cd {getenv("path_scripts")};./log_{action}.sh {self.args["server_name"]} {self.args["component"]};"'''
        print("@@ LOG CHANGE LEVEL COMMAND @@\n\n")
        print(batcmd)
        output = subprocess.check_output(batcmd, shell=True, text=True)
        print("@@ LOG CHANGE LEVEL OUTPUT @@\n\n")
        print(output)
        return {"response_message": f"Log level {action}d.",
                 "status": 200,
                 "mimetype": "application/json"}


    def list_log_level(self):
        if self.isADM:
            batcmd = f'''plink -batch siebel@{self.args["serv_ip"]} -pw {self.args["servpw"]} "cd {getenv("path_scripts")};./log_list.sh {self.args["server_name"]} {self.args["component"]};"'''
        else:
            batcmd = f'''plink -hostkey "{self.args["winscp_hostkey"]}" -batch siebel@{self.args["serv_ip"]} -pw {self.args["servpw"]} "cd {getenv("path_scripts")};./log_list.sh {self.args["server_name"]} {self.args["component"]};"'''
        print("@@ LOG LIST LEVEL COMMAND @@\n\n")
        print(batcmd)
        output = subprocess.check_output(batcmd, shell=True, text=True).split()
        print("@@ LOG LIST LEVEL OUTPUT @@\n\n")
        print(output)
        print("There are", output.count("0"), "amount of zeroes.")
        print("There are", output.count("5"), "amount of fives.")
        return output


    def request_log(self):
        self.change_log_level(Change_log_action.DECREASE)
        files = find_file(self.args)
        assert files, "Couldn't find any files."
        files_str = ""
        for _file in files:
            if self.isADM:
                batcmd = f'''"C:\\Program Files (x86)\\WinSCP\\WinSCP.exe" /command "option batch on" "option confirm off" "open siebel:"{self.args["servpw"]}"@"{self.args["serv_ip"]}"" "get {self.args["path_unix_log"]}/{_file} E:\\LogCopyAutomation\\{_file}" "/log={self.args["path_log"]}\\LogCopy_{_file}"'''
            else:
                batcmd = f'''"C:\\Program Files (x86)\\WinSCP\\WinSCP.exe" /command "option batch on" "option confirm off" "open -hostkey=""{self.args["winscp_hostkey"]}"" siebel:"{self.args["servpw"]}"@"{self.args["serv_ip"]}"" "get {self.args["path_unix_log"]}/{_file} E:\\LogCopyAutomation\\{_file}" "/log={self.args["path_log"]}\\LogCopy_{_file}"'''
            print("@@ WINSCP OUTPUT @@\n\n")
            subprocess.check_output(batcmd, shell=True, text=True)
            files_str += _file + " "
        batcmd = f""""C:\\Program Files\\7-Zip\\7z.exe" a {self.args["keyword"]}.zip {files_str}-mx5"""
        print("@@ 7z OUTPUT @@\n\n")
        chdir("E:\\LogCopyAutomation")
        subprocess.check_output(batcmd, shell=True, text=True)
        for _file in files:
            subprocess.check_output(f"del {_file}", shell=True, text=True)
        chdir(path_project)
        return glob(path.join(getenv("path_file_to_upload"), self.req_data.get("keyword") + ".zip"))[-1]

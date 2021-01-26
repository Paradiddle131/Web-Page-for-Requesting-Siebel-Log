import subprocess
from glob import glob
from json import load, dump
from logging import error, debug
from os import getenv, getcwd, path, chdir
from time import time

from dotenv import load_dotenv

path_project = getcwd()
path_batch = path.join(path_project, "plink_.bat")
response = {}
open_machines = []
isTest = False


class Response_type:
    LOG_LEVEL_INCREASED = "LOG_LEVEL_INCREASED"
    LOG_LEVEL_DECREASED = "LOG_LEVEL_DECREASED"
    FILE = "FILE"

class Change_log_action:
    INCREASE = "increase"
    DECREASE = "decrease"


def return_response_message(response_message, status):
    return {"response_message": response_message,
            "status": status}


class Siebel:
    load_dotenv("config.env")
    def __init__(self, req_data):
        if type(req_data["isAdm"]) == str:
            self.isADM = True if req_data["isAdm"].lower() == "true" else False
        else:
            self.isADM = req_data["isAdm"]
        self.req_data = req_data
        with open("static/data/servers.json", "r") as f:
            self.servers = load(f)
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
                "component_name": self.get_request_attribute("component_name"),
                "component": self.get_request_attribute("component"),
            }
        self.args.update(
            {
                "path_log": getenv("path_log"),
                "path_unix_log": getenv("path_unix_log"),
                "keyword": self.req_data.get("keyword"),
                "machine_no": self.req_data.get("machine_no")
            }
        )


    def get_request_attribute(self, attribute_name):
        try:
            return self.servers[int(self.req_data.get("machine_no")) - 1][attribute_name]
        except:
            error(f"Error retrieving attribute with attribute name: {attribute_name}, on machine #{self.req_data.get('machine_no')}", exc_info=True)


    def find_keyword(self):
        try:
            if self.isADM:
                batcmd = '''plink -batch siebel@{} -pw {} "cd {};echo $(ls -t | egrep '{}');"'''.format(self.args["serv_ip"], self.args["servpw"], self.args["path_unix_log"], "_[0-9]{9}\.log")
            else:
                if int(self.args["machine_no"]) < 7:
                    regex_pattern = "_[0-9]{9}\.log"
                else:
                    regex_pattern = "_[0-9]{7}\.log"
                batcmd = '''plink -hostkey "{}" -batch siebel@{} -pw {} "cd {};echo $(ls -t | egrep '{}');"'''.format(self.args["winscp_hostkey"], self.args["serv_ip"], self.args["servpw"], self.args["path_unix_log"], regex_pattern)
            debug(f"@@ FIND KEYWORD COMMAND @@\n{batcmd}")
            output = subprocess.check_output(batcmd, shell=True, text=True).split()[0].split('_')[-1][:-4]
            debug(f"@@ FIND KEYWORD OUTPUT @@\n{output}")
            return output
        except:
            error(f"Error finding keyword on machine #{self.req_data.get('machine_no')}.", exc_info=True)

    def find_file(self):
        try:
            if self.isADM:
                batcmd = '''plink -batch siebel@{} -pw {} "cd {};echo $(grep -l '{}' *.log);"'''.format(self.args["serv_ip"], self.args["servpw"], self.args["path_unix_log"], self.args["keyword"])
            else:
                batcmd = '''plink -hostkey "{}" -batch siebel@{} -pw {} "cd {};echo $(grep -l '{}' *.log);"'''.format(self.args["winscp_hostkey"], self.args["serv_ip"], self.args["servpw"], self.args["path_unix_log"], self.args["keyword"])
            debug(f"@@ FIND FILE COMMAND @@\n{batcmd}")
            output = subprocess.check_output(batcmd, shell=True, text=True).split()
            debug(f"@@ FIND FILE OUTPUT @@\n{output}")
            return output
        except:
            error(f"Error finding file on machine #{self.req_data.get('machine_no')} with keyword: \"{self.args['keyword']}\".", exc_info=True)


    def change_log_level(self, action):
        """action: type:Change_log_action, "INCREASE" or "DECREASE" """
        try:
            if action != Change_log_action.INCREASE and action != Change_log_action.DECREASE:
                debug(f"Wrong argument passed: {action}")
                return None
            if self.isADM:
                batcmd = f'''plink -batch siebel@{self.args["serv_ip"]} -pw {self.args["servpw"]} "cd {getenv("path_scripts")};./log_{action}.sh {self.args["server_name"]} {self.args["component"]};"'''
            else:
                batcmd = f'''plink -hostkey "{self.args["winscp_hostkey"]}" -batch siebel@{self.args["serv_ip"]} -pw {self.args["servpw"]} "cd {getenv("path_scripts")};./log_{action}.sh {self.args["server_name"]} {self.args["component"]};"'''
            debug(f"@@ LOG CHANGE LEVEL COMMAND @@\n{batcmd}")
            output = subprocess.check_output(batcmd, shell=True, text=True)
            if not output:
                return return_response_message("Error changing the log level.", status=500)
            debug(f"@@ LOG CHANGE LEVEL OUTPUT @@\n{output}")
            with open("static/data/servers.json", "w+") as f:
                self.servers[int(self.req_data.get("machine_no")) - 1].update({"log_level_status": "5" if action == Change_log_action.INCREASE else "0"})
                self.servers[int(self.req_data.get("machine_no")) - 1].update({"log_level_last_updated": str(time())})
                dump(self.servers, f)
            return {"response_message": f"Log level {action}d.",
                    "status": 200}
        except:
            error(f"Error changing log level on machine #{self.req_data.get('machine_no')}.", exc_info=True)


    def list_log_level(self):
        try:
            if self.isADM:
                batcmd = f'''plink -batch siebel@{self.args["serv_ip"]} -pw {self.args["servpw"]} "cd {getenv("path_scripts")};./log_list.sh {self.args["server_name"]} {self.args["component"]};"'''
            else:
                batcmd = f'''plink -hostkey "{self.args["winscp_hostkey"]}" -batch siebel@{self.args["serv_ip"]} -pw {self.args["servpw"]} "cd {getenv("path_scripts")};./log_list.sh {self.args["server_name"]} {self.args["component"]};"'''
            debug(f"@@ LOG LIST LEVEL COMMAND @@\n{batcmd}")
            output = subprocess.check_output(batcmd, shell=True, text=True).split()
            debug(f"@@ LOG LIST LEVEL OUTPUT @@\n{output}")
            debug(f"There are {output.count('0')} amount of zeroes.")
            debug(f"There are {output.count('5')} amount of fives.")
            return output
        except:
            error(f"Error listing log level on machine #{self.req_data.get('machine_no')}.", exc_info=True)

    def request_log(self):
        try:
            files = self.find_file()
            if not files:
                return return_response_message("Couldn't find any files.", status=500)
            files_str = ""
            for _file in files:
                if self.isADM:
                    batcmd = f'''"C:\\Program Files (x86)\\WinSCP\\WinSCP.exe" /command "option batch on" "option confirm off" "open siebel:"{self.args["servpw"]}"@"{self.args["serv_ip"]}"" "get {self.args["path_unix_log"]}/{_file} E:\\LogCopyAutomation\\{_file}" "/log={self.args["path_log"]}\\LogCopy_{_file}"'''
                else:
                    batcmd = f'''"C:\\Program Files (x86)\\WinSCP\\WinSCP.exe" /command "option batch on" "option confirm off" "open -hostkey=""{self.args["winscp_hostkey"]}"" siebel:"{self.args["servpw"]}"@"{self.args["serv_ip"]}"" "get {self.args["path_unix_log"]}/{_file} E:\\LogCopyAutomation\\{_file}" "/log={self.args["path_log"]}\\LogCopy_{_file}"'''
                debug(f"@@ WINSCP COMMAND @@\n{batcmd}")
                output = subprocess.check_output(batcmd, shell=True, text=True)
                debug(f"@@ WINSCP OUTPUT @@\n{output}")
                files_str += _file + " "
            batcmd = f""""C:\\Program Files\\7-Zip\\7z.exe" a "{self.args["keyword"]}.zip" {files_str}-mx5"""
            debug(f"@@ 7z COMMAND @@\n{batcmd}")
            chdir("E:\\LogCopyAutomation")
            output = subprocess.check_output(batcmd, shell=True, text=True)
            debug(f"@@ 7z OUTPUT @@\n{output}")
            for _file in files:
                subprocess.check_output(f"del {_file}", shell=True, text=True)
            chdir(path_project)
            return glob(path.join(getenv("path_file_to_upload"), self.req_data.get("keyword") + ".zip"))[-1]
        except:
            error(f"Error requesting log on machine #{self.req_data.get('machine_no')} with keyword: \"{self.args['keyword']}\".", exc_info=True)
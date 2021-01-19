import socket
from logging import FileHandler, basicConfig, info, error, DEBUG, debug
from os import getenv, chdir, system
from subprocess import check_output
from dotenv import load_dotenv

import servicemanager
import win32event
import win32service
import win32serviceutil


class AppServerSvc(win32serviceutil.ServiceFramework):
    load_dotenv('config.env')
    _svc_name_ = "SiebelLogService"
    _svc_display_name_ = "Siebel Log Service"
    task_name = getenv("host_address") + ":" + getenv("host_port")

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        res = check_output(f"netstat -ano | findstr {self.task_name}", shell=True, text=True)
        debug(res, exc_info=True)
        pid = res.replace("\n", "")[-5:]
        res = check_output(f"taskkill /PID {pid} /F")
        debug(res, exc_info=True)
        info(f"Service has been stopped with PID: {pid}", exc_info=True)
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        chdir("C:\\op_tools\\Siebel_Log_Page")
        info(f"Starting service: \"{self._svc_name_}\"", exc_info=True)
        system("python server.py")


if __name__ == '__main__':
    basicConfig(handlers=[FileHandler(encoding='utf-8', filename='win_service.log', mode='w')],
                level=DEBUG,
                format=u'%(levelname)s - %(name)s - %(asctime)s: %(message)s')
    try:
        win32serviceutil.HandleCommandLine(AppServerSvc)
    except Exception as e:
        error(f"Exception has been written to text file.", exc_info=True)

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import os

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "SiebelLogService"
    _svc_display_name_ = "Siebel Log Service"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
        os.chdir("C:\\op_tools\\Siebel_Log_Page")
        os.system("python server.py")

if __name__ == '__main__':
    try:
        win32serviceutil.HandleCommandLine(AppServerSvc)
    except Exception as e:
        os.system("echo Exception! > exception.txt")
        os.system(f"{e} > service_error.txt") 
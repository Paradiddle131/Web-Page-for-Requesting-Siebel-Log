@echo OFF
set PATH=%PATH%;C:\Program Files\Putty
set serv_ip=%1
set servpw=%2
set path_log=%3
set path_unix_log=%4
set winscp_hostkey=%5

set action=%6
set keyword=%7
set machine_no=%8
set server_name=%9
shift
set time_log=%9
shift
set component=%9
echo starting...

FOR /F "delims=" %%i IN ('plink -batch siebel@%serv_ip% -pw %servpw% "cd %path_unix_log%;echo $(grep -l %keyword% %component%*.log);" "exit"') DO set file_name=%%i
echo file_name: %file_name%

IF %action%=="OPEN_LOG" (
	echo Opening log %%5 on server: %server_name%
	plink -batch siebel@%serv_ip% -pw %servpw% "cd /home/siebel/script;./log_increase.sh '%server_name%' crm;" "exit"
)

IF %action%=="CLOSE_LOG" (
	echo Closing log %%0 on server: %server_name%
	plink -batch siebel@%serv_ip% -pw %servpw% "cd /home/siebel/script;./log_decrease.sh '%server_name%' crm;" "exit"
)

IF %action%=="REQUEST_LOG" (
	"C:\Program Files (x86)\WinSCP\WinSCP.exe" /command "option batch on" "option confirm off" "open -hostkey="%winscp_hostkey%" siebel:%servpw%@%serv_ip%" "get %path_unix_log%/%file_name% E:\LogCopyAutomation\%time_log%_%file_name%" "/log=%path_log%\LogCopy_%time_log%_%file_name%" "exit"
	echo %time_log:~1,-1%_%file_name% copied successfully to E:/ drive.
	exit
	timeout /t 3
	E:
	cd E:\LogCopyAutomation\
	"C:\Program Files\7-Zip\7z.exe" a %time_log:~1,-1%_%file_name:~0,-4%.zip E:\LogCopyAutomation\%time_log:~1,-1%_%file_name% -mx5
	del %time_log:~1,-1%_%file_name%
)
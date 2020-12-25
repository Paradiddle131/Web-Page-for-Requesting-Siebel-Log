@echo OFF
set PATH=%PATH%;C:\Program Files\Putty
set serv_ip=%1
set servpw=%2
set path_log=%3
set path_unix_log=%4
set hostkey=%5

set action=%6
set keyword=%7
set machine_no=%8
set server_name=%9
shift
set time_log=%9
shift
set component=%9
echo starting...

echo FOR /F "tokens=*" %%i IN ('plink -hostkey %hostkey% -batch siebel@%serv_ip% -pw %servpw% "cd %path_unix_log%;echo $(grep -l %keyword% %component:"=%*.log);" "exit"') DO ( call set "files=%%files%% %%i")
FOR /F "tokens=*" %%i IN ('plink -hostkey %hostkey% -batch siebel@%serv_ip% -pw %servpw% "cd %path_unix_log%;echo $(grep -l %keyword% %component:"=%*.log);" "exit"') DO ( call set "files=%%files%%%%i")
echo files: %files%

IF %action%=="OPEN_LOG" (
	echo Opening log %%5 on server: %server_name%
	plink -hostkey %hostkey% -batch siebel@%serv_ip% -pw %servpw% "cd /home/siebel/script;./log_increase.sh '"SBL_PRO01"' crm;" "exit"
)

IF %action%=="CLOSE_LOG" (
	echo Closing log %%0 on server: %server_name%
	plink -hostkey %hostkey% -batch siebel@%serv_ip% -pw %servpw% "cd /home/siebel/script;./log_decrease.sh '%server_name%' crm;" "exit"
)

IF %action%=="REQUEST_LOG" (
	setlocal enabledelayedexpansion
	set serv_ip=%serv_ip:"=%
	set servpw=%servpw:"=%
	set hostkey=%hostkey:"=%
	set path_unix_log=%path_unix_log:"=%
	set path_log=%path_log:"=%
	set files=%files:"=%
	echo "C:\Program Files (x86)\WinSCP\WinSCP.exe" /command "option batch on" "option confirm off" "open -hostkey="%hostkey%" siebel:%servpw%@%serv_ip%" "get %path_unix_log%/%files% E:\LogCopyAutomation\%files%" "/log=%path_log%\LogCopy_%files%" "exit"
		"C:\Program Files (x86)\WinSCP\WinSCP.exe" /command "option batch on" "option confirm off" "open -hostkey="%hostkey%" siebel:%servpw%@%serv_ip%" "get %path_unix_log%/%files% E:\LogCopyAutomation\%files%" "/log=%path_log%\LogCopy_%files%" "exit"
	echo %files% copied successfully to E:/ drive.
	E:
	cd E:\LogCopyAutomation\
	echo "C:\Program Files\7-Zip\7z.exe" a %keyword%.zip %files% -mx5
	"C:\Program Files\7-Zip\7z.exe" a %keyword%.zip %files% -mx5
	exit
	del %files%
)
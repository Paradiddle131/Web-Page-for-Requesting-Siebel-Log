from datetime import datetime, timedelta
from json import load, loads, dumps
from logging import FileHandler, basicConfig, info, error, DEBUG
from time import ctime

from flask import request, Flask
from timeloop import Timeloop

from siebel import Change_log_action, Siebel

app = Flask(__name__)

tl = Timeloop()


@tl.job(interval=timedelta(minutes=5))
def update_log_level_status():
    info("\n" + ctime())
    for machine_no in [str(x) for x in range(1, 15)]:
        try:
            with open("static/data/servers.json") as f:
                servers = load(f)
            last_update = datetime.fromtimestamp(int(servers[int(machine_no) - 1]["log_level_last_updated"].split('.')[0]))
            time_difference = divmod((datetime.now() - last_update).seconds, 60)[0]
            if servers[int(machine_no) - 1]["log_level_status"] == '5' and \
                time_difference < 30:
                info(f"Skipping. Log level has been 5 on machine #{machine_no} for {time_difference} minutes.")
            elif servers[int(machine_no) - 1]["log_level_status"] == '5' and \
                time_difference >= 30:
                with app.test_request_context('/', json=dumps({"machine_no": machine_no, "isAdm": False, "Server_action": "close_log"})):
                    siebel = Siebel(req_data=loads(request.json))
                siebel.change_log_level(Change_log_action.DECREASE)
                info(f"Log level on machine #{machine_no} has been changed to 0 due to 30+ minutes of continuous activeness since: {last_update}.")
            else:
                info(f"Skipping. It's been {time_difference} minutes since the last check on machine #{machine_no}.")
        except:
            error(f"Error on machine #{machine_no}.", exc_info=True)

if __name__ == '__main__':
    basicConfig(handlers=[FileHandler(encoding='utf-8', filename='log_status.log', mode='w')],
                level=DEBUG,
                format=u'%(levelname)s - %(name)s - %(asctime)s: %(message)s')
    tl.start(block=True)

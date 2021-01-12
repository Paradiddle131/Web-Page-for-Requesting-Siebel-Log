from datetime import datetime, timedelta
from json import load, loads, dumps
from time import ctime

from flask import request, Flask
from timeloop import Timeloop

from siebel import Change_log_action, Siebel

app = Flask(__name__)

tl = Timeloop()


@tl.job(interval=timedelta(minutes=5))
def update_log_level_status():
    print("\n" + ctime())
    for machine_no in [str(x) for x in range(1, 15)]:
        with open("static/data/servers.json") as f:
            servers = load(f)
        last_update = datetime.fromtimestamp(int(servers[int(machine_no) - 1]["log_level_last_updated"].split('.')[0]))
        time_difference = divmod((datetime.now() - last_update).seconds, 60)[1]
        if servers[int(machine_no) - 1]["log_level_status"] == '5' and \
            time_difference >= 0:
            with app.test_request_context('/', json=dumps({"machine_no": machine_no, "isAdm": False, "Server_action": "close_log"})):
                siebel = Siebel(req_data=loads(request.json))
            siebel.change_log_level(Change_log_action.DECREASE)
            print(f"Log level on machine #{machine_no} has been changed to 0 due to 30+ minutes of continuous activeness since: {last_update}.")
        else:
            print(f"Skipping. It's been {time_difference} minutes since the last check on machine #{machine_no}.")


if __name__ == '__main__':
    tl.start(block=True)

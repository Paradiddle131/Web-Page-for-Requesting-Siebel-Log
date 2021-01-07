import json
import unittest

from flask import request, Flask

from siebel import Siebel, Change_log_action

app = Flask(__name__)

class Request:
    def __init__(self, request_dict):
        self.request_mock = request_dict

    def get_data(self):
        return json.dumps(self.request_mock)

    def set_data(self, key, value):
        self.request_mock.update({key: value})

class TestServer(unittest.TestCase):
    def test_a_increase_log_level_should_success(self):
        '''Testing if log level increased to 5...'''
        request_obj.set_data("Server_action", "open_log")
        with app.test_request_context('/open_log', json=request_obj.get_data()):
            data = json.loads(request.json)
            print(data)
        siebel = Siebel(req_data=data, isADM=False)
        siebel.change_log_level(Change_log_action.INCREASE)
        count = siebel.list_log_level().count("5")
        print(count)
        self.assertGreaterEqual(count, 180, msg=f"Error increasing log level on machine pro{data['machine_no']}")

    def test_b_decrease_log_level_should_success(self):
        '''Testing if log level decreased to 0...'''
        request_obj.set_data("Server_action", "close_log")
        with app.test_request_context('/close_logs', json=request_obj.get_data()):
            data = json.loads(request.json)
            print(data)
        siebel = Siebel(req_data=data, isADM=False)
        siebel.change_log_level(Change_log_action.DECREASE)
        count = siebel.list_log_level().count("0")
        print(count)
        self.assertGreaterEqual(count, 180, msg=f"Error decreasing log level on machine pro{data['machine_no']}")

    def test_c_request_log_should_success(self):
        with app.test_request_context('/close_logs', json=request_obj.get_data()):
            data = json.loads(request.json)
            print(data)
        siebel = Siebel(req_data=data, isADM=False)
        self.assertIsNotNone(siebel.request_log())


if __name__ == '__main__':
    request_obj = Request({"keyword": "404751504", "machine_no": "3", "component": "callcenter_enu"})
    unittest.main()
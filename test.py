import json
import unittest
from logging import FileHandler, basicConfig, DEBUG

from flask import request, Flask
from parameterized import parameterized

from siebel import Siebel, Change_log_action

app = Flask(__name__)
machines_list = [str(x) for x in range(1, 15)]

class Request:
    def __init__(self, request_dict):
        self.request_mock = request_dict

    def __getitem__(self, attribute_name):
        return self.request_mock[attribute_name]

    def get_data(self):
        return json.dumps(self.request_mock)

    def set_data(self, key, value):
        self.request_mock.update({key: value})


def setup(machine_no):
    request_obj.set_data("machine_no", machine_no)
    request_obj.set_data("isAdm", False)
    with app.test_request_context('/', json=request_obj.get_data()):
        siebel = Siebel(req_data=json.loads(request.json))
    keyword = siebel.find_keyword()
    request_obj.set_data("keyword", keyword)
    request_obj.set_data("component", "crm" if int(machine_no) <= 7 else "prm")
    # Must call siebel once again to append recent parameters to siebel object
    with app.test_request_context('/', json=request_obj.get_data()):
        siebel = Siebel(req_data=json.loads(request.json))
    return siebel, keyword


def find_keyword(siebel):
    return siebel.find_keyword()


def change_log_level(siebel, change_log_action):
    siebel.change_log_level(change_log_action)
    return siebel.list_log_level().count('5' if change_log_action == Change_log_action.INCREASE else '0')


def request_log(siebel):
    return siebel.request_log()


class TestServer(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @parameterized.expand(machines_list)
    def test_all_actions(self, machine_no):
        siebel, keyword = setup(machine_no)
        self.assertIsNotNone(keyword, "Error finding keyword")
        count = change_log_level(siebel, Change_log_action.INCREASE)
        self.assertGreaterEqual(count, 180, msg=f"Error {Change_log_action.INCREASE[:-1]}ing log level on machine pro{machine_no}.")
        count = change_log_level(siebel, Change_log_action.DECREASE)
        self.assertGreaterEqual(count, 180, msg=f"Error {Change_log_action.DECREASE[:-1]}ing log level on machine pro{machine_no}.")
        file_name = request_log(siebel)
        self.assertIsNotNone(file_name, msg=f"Error requesting log file with keyword: {keyword} on machine pro{machine_no}.")


if __name__ == '__main__':
    basicConfig(handlers=[FileHandler(encoding='utf-8', filename='test.log', mode='w')],
                level=DEBUG,
                format=u'%(levelname)s - %(name)s - %(asctime)s: %(message)s')
    request_obj = Request({"isAdm": False})
    unittest.main()
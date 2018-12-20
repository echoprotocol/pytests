import json
import os

from websocket import create_connection

import lemoncheesecake.api as lcc

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..//resources")
ECHO_DEV = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
METHOD = json.load(open(os.path.join(RESOURCES_DIR, "echo_methods.json")))
EXPECTED = json.load(open(os.path.join(RESOURCES_DIR, "expected_data.json")))
CALL_FORMAT = {"id": 0, "method": "call", "params": []}


class BaseTest(object):
    login = "login"

    def __init__(self):
        self.ws = create_connection(ECHO_DEV)
        self.resp = None
        self.api_id = 0
        self.identifier = None

    @staticmethod
    def get_request(method_name, params=None):
        # Params must be list
        request = [1, method_name]
        if params is None:
            request.extend([METHOD[method_name]])
            return request
        else:
            request.extend([params])
            return request

    @staticmethod
    def get_expected(variable_name):
        return EXPECTED[variable_name]

    def call_method(self, method, call_back=None):
        # Returns the api method call
        self.api_id += 1
        if call_back is None:
            CALL_FORMAT["id"] = self.api_id
            CALL_FORMAT["params"] = method
            return CALL_FORMAT
        else:
            CALL_FORMAT["id"] = self.api_id
            CALL_FORMAT["params"][0] = call_back
            for i in range(1, 3):
                CALL_FORMAT["params"][i] = method[i]
            return CALL_FORMAT

    def send_request(self, request, call_back=None):
        # Send request to server
        if call_back is None:
            self.ws.send(json.dumps(self.call_method(request)))
            return self.ws
        else:
            self.ws.send(json.dumps(self.call_method(request, call_back)))
            return self.ws

    def get_response(self):
        # Receive answer from server
        self.resp = json.loads(self.ws.recv())
        lcc.log_info("Received: \n{}".format(json.dumps(self.resp, indent=4)))
        return self.resp

    def get_identifier(self, resp):
        # Get identifier of api
        self.identifier = resp["result"]

    @staticmethod
    def login_status(response):
        # Check authorization status
        if "result" in response:
            if response["result"]:
                lcc.log_info("Login successful")
            else:
                lcc.log_info("Login failed")
        else:
            lcc.log_error("Login failed")

    def login_echo(self):
        # Login to Echo
        lcc.set_step("Login to Echo")
        self.send_request(self.get_request(self.login))
        resp = self.get_response()
        self.login_status(resp)

    def setup_suite(self):
        # Check status of connection
        lcc.set_step("Open connection")
        if self.ws is not None:
            lcc.log_url(ECHO_DEV)
            lcc.log_info("Connection successfully created")
            self.login_echo()
        else:
            lcc.log_error("Connection not established")

    def teardown_suite(self):
        # Close connection to WebSocket
        lcc.set_step("Close connection")
        self.ws.close()
        lcc.log_info("Connection closed")

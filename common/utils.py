import json
import os

from websocket import create_connection

import lemoncheesecake.api as lcc

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..//resources")
ECHO_DEV = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
METHOD = json.load(open(os.path.join(RESOURCES_DIR, "echo_methods.json")))
EXPECTED = json.load(open(os.path.join(RESOURCES_DIR, "expected_data.json")))


class BaseTest(object):
    login_api = "login"

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
        # Return data from json file
        return EXPECTED[variable_name]

    @staticmethod
    def get_template():
        # Return call method format
        return {"id": 0, "method": "call", "params": []}

    def call_method(self, method, call_back=None):
        # Returns the api method call
        self.api_id += 1
        call_template = self.get_template()
        if call_back is None:
            call_template["id"] = self.api_id
            call_template["params"] = method
            return call_template
        else:
            call_template["id"] = self.api_id
            call_template["params"].append(call_back)
            for i in range(1, len(method)):
                call_template["params"].append(method[i])
            return call_template

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

    def get_identifier(self, api):
        # Initialise identifier for api
        lcc.set_step("Get {} identifier".format(api))
        self.send_request(self.get_request(api))
        resp = self.get_response()
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
        self.send_request(self.get_request(self.login_api))
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

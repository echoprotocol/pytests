import json
import os

from websocket import create_connection

import lemoncheesecake.api as lcc

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..//resources")
ECHO_DEV = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
METHOD = json.load(open(os.path.join(RESOURCES_DIR, "echo_methods.json")))
EXPECTED = json.load(open(os.path.join(RESOURCES_DIR, "expected_data.json")))


class BaseTest(object):
    _login_api = "login"
    _database_api = "database"
    _asset_api = "asset"
    _history_api = "history"
    _network_broadcast_api = "network_broadcast"

    def __init__(self):
        self.__ws = create_connection(ECHO_DEV)
        self.__resp = None
        self.__request = None
        self.__api_id = 0
        self._identifier = None

    def get_request(self, method_name, params=None):
        # Params must be list
        self.__request = [1, method_name]
        if params is None:
            self.__request.extend([METHOD[method_name]])
            return self.__request
        else:
            self.__request.extend([params])
            return self.__request

    @staticmethod
    def get_expected(variable_name):
        # Return data from json file
        return EXPECTED[variable_name]

    @staticmethod
    def get_template():
        # Return call method format
        return {"id": 0, "method": "call", "params": []}

    def __call_method(self, method, call_back=None):
        # Returns the api method call
        self.__api_id += 1
        call_template = self.get_template()
        if call_back is None:
            call_template["id"] = self.__api_id
            call_template["params"] = method
            return call_template
        else:
            call_template["id"] = self.__api_id
            call_template["params"].append(call_back)
            for i in range(1, len(method)):
                call_template["params"].append(method[i])
            return call_template

    def send_request(self, request, call_back=None):
        # Send request to server
        if call_back is None:
            self.__ws.send(json.dumps(self.__call_method(request)))
            return self.__ws
        else:
            self.__ws.send(json.dumps(self.__call_method(request, call_back)))
            return self.__ws

    def get_response(self):
        # Receive answer from server
        self.__resp = json.loads(self.__ws.recv())
        lcc.log_info("Received: \n{}".format(json.dumps(self.__resp, indent=4)))
        return self.__resp

    def get_identifier(self, api):
        # Initialise identifier for api
        lcc.set_step("Get {} identifier".format(api))
        self.send_request(self.get_request(api))
        self.__resp = self.get_response()
        self._identifier = self.__resp["result"]
        return self._identifier

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

    def __login_echo(self):
        # Login to Echo
        lcc.set_step("Login to Echo")
        self.send_request(self.get_request(self._login_api))
        self.__resp = self.get_response()
        self.login_status(self.__resp)

    def setup_suite(self):
        # Check status of connection
        lcc.set_step("Open connection")
        if self.__ws is not None:
            lcc.log_url(ECHO_DEV)
            lcc.log_info("Connection successfully created")
            self.__login_echo()
        else:
            lcc.log_error("Connection not established")

    def teardown_suite(self):
        # Close connection to WebSocket
        lcc.set_step("Close connection")
        self.__ws.close()
        lcc.log_info("Connection closed")

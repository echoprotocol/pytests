import json
import os

from websocket import create_connection

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_integer, is_str, is_

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..//resources")
echo_dev = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]


class BaseTest(object):
    def __init__(self):
        self.ws = create_connection(echo_dev)
        self.resp = None
        self.api_id = 0
        self.identifier = None
        self.echo_api = "echo_apis.json"
        self.login = "LOGIN"
        self.call_format = {"id": 0, "method": "call", "params": [{}, {}, {}]}

    @staticmethod
    def get_data(file_name, variable_name, params=None):
        # Params must be list
        if params is None:
            return json.load(open(os.path.join(RESOURCES_DIR, file_name)))[variable_name]
        else:
            data = json.load(open(os.path.join(RESOURCES_DIR, file_name)))[variable_name]
            data.insert(2, params)
            return data

    def call_method(self, method, call_back=None):
        # Method returns the api method call
        self.api_id += 1
        if call_back is None:
            self.call_format["id"] = self.api_id
            for i in range(3):
                self.call_format["params"][i] = method[i]
            return self.call_format
        else:
            self.call_format["id"] = self.api_id
            self.call_format["params"][0] = call_back
            for i in range(1, 3):
                self.call_format["params"][i] = method[i]
            return self.call_format

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

    def check_resp_format(self, response):
        # Method check the validity of the response from the server
        check_that_in(
            response,
            "id", is_integer(),
            "id", is_(self.api_id),
            "jsonrpc", is_str(),
            "jsonrpc", is_("2.0")
        )

    def check_and_get_identifier(self, response):
        # Check the validity of the result
        check_that_in(
            response,
            "result", is_integer(),
        )
        self.identifier = response["result"]

    @staticmethod
    def login_status(response):
        # Method check authorization status
        if "result" in response:
            if response["result"]:
                lcc.log_info("Login successful")
            else:
                lcc.log_info("Login failed")
        else:
            lcc.log_error("Login failed")

    def login_echo(self):
        lcc.set_step("Login to Echo")
        self.send_request(self.get_data(self.echo_api, self.login))
        resp = self.get_response()
        self.login_status(resp)

    def setup_suite(self):
        # Check status of connection
        if self.ws is not None:
            lcc.log_url(echo_dev)
            lcc.log_info("Connection successfully created")
        else:
            lcc.log_error("Connection not established")

    def teardown_suite(self):
        # Close connection to WebSocket
        lcc.set_step("Close connection")
        self.ws.close()
        lcc.log_info("Connection closed")

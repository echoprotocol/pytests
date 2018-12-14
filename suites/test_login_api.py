import json
import os

from websocket import create_connection

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_bool, is_integer, is_str, is_

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..//resources")
echo_dev = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
login_empty_params = json.load(open(os.path.join(RESOURCES_DIR, "login_methods.json")))["LOGIN_EMPTY_PARAMS"]
login_valid_params = json.load(open(os.path.join(RESOURCES_DIR, "login_methods.json")))["LOGIN_VALID_PARAMS"]

SUITE = {
    "description": "Test 'Login API'"
}


class BaseTest(object):
    def __init__(self):
        self.ws = create_connection(echo_dev)
        self.resp = None
        self.api_id = 0
        self.call_format = {"id": 0, "method": "call", "params": [{}, {}, {}]}

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


@lcc.suite("Test login method")
class TestLoginMethod(BaseTest):
    def __init__(self):
        super().__init__()

    @lcc.test("Login with empty parameters")
    def test_login_with_empty_params(self):
        # Login to Echo
        self.send_request(login_empty_params)

        # Receive authorization response
        resp = self.get_response()

        # Check response
        lcc.set_step("Check response with empty data")
        self.check_resp_format(resp)
        check_that_in(
            resp,
            "result", is_bool()
        )

        # Check authorization status
        lcc.set_step("Check that login successful")
        self.login_status(resp)

    @lcc.test("Login with valid parameters")
    def test_login_with_valid_params(self):
        # Login to Echo
        lcc.set_step("Login to the Full Node with valid params")
        self.send_request(login_valid_params)

        # Receive authorization response
        resp = self.get_response()

        # Check response
        lcc.set_step("Check response with empty data")
        self.check_resp_format(resp)

        # Check authorization status
        lcc.set_step("Check that login successful")
        self.login_status(resp)

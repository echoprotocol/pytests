import json
import os

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_, is_bool, is_integer, is_str
from websocket import create_connection

call_format = {"id": 0, "method": "call", "params": [{}, {}, {}]}  # id, method_name, data
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..//resources")
echo_dev = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
login_empty_params = json.load(open(os.path.join(RESOURCES_DIR, "login_methods.json")))["LOGIN_EMPTY_PARAMS"]
login_valid_params = json.load(open(os.path.join(RESOURCES_DIR, "login_methods.json")))["LOGIN_VALID_PARAMS"]

SUITE = {
    "description": "Test 'Login API'"
}


@lcc.suite("Test login method")
class TestLoginMethod:
    def __init__(self):
        self.ws = create_connection(echo_dev)
        self.api_id = 0

    def call_method(self, method, call_back=None):
        # Method returns the api method call
        self.api_id += 1
        if call_back is None:
            call_format["id"] = self.api_id
            for i in range(3):
                call_format["params"][i] = method[i]
            return call_format
        else:
            call_format["id"] = self.api_id
            call_format["params"][0] = call_back
            for i in range(1, 3):
                call_format["params"][i] = method[i]
            return call_format

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

    @lcc.test("Login with empty parameters")
    def test_login_with_empty_params(self):
        # Login to Echo
        lcc.set_step("Login to the Full Node with empty params")
        self.ws.send(json.dumps(self.call_method(login_empty_params)))

        # Receive authorization response
        resp = json.loads(self.ws.recv())
        lcc.log_info("Received: \n{}".format(json.dumps(resp, indent=4)))

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
        self.ws.send(json.dumps(self.call_method(login_valid_params)))

        # Receive authorization response
        resp = json.loads(self.ws.recv())
        lcc.log_info("Received: \n{}".format(json.dumps(resp, indent=4)))

        # Check response
        lcc.set_step("Check response with empty data")
        self.check_resp_format(resp)

        # Check authorization status
        lcc.set_step("Check that login successful")
        self.login_status(resp)

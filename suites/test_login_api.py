import json
import os

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_, is_bool, is_integer, is_str
from websocket import create_connection

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..//resources")
echo_dev = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
login_empty_params = json.load(open(os.path.join(RESOURCES_DIR, "login_methods.json")))["LOGIN_EMPTY_PARAMS"]

SUITE = {
    "description": "Test 'Login API'"
}


@lcc.suite("Test login method")
class TestLoginMethod:
    def __init__(self):
        self.ws = create_connection(echo_dev)

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
        lcc.log_info("Connection closed ")

    @lcc.test("Login with empty parameters")
    def test_login_with_empty_params(self, generate_number_between):
        # Login to Echo
        lcc.set_step("Login to the Full Node")
        login_empty_params["id"] = generate_number_between
        self.ws.send(json.dumps(login_empty_params))

        # Receive authorization response
        resp = json.loads(self.ws.recv())
        lcc.log_info("Received: \n{}".format(json.dumps(resp, indent=4)))

        # Check response
        lcc.set_step("Check response with empty data")
        check_that_in(
            resp,
            "id", is_integer(),
            "id", is_(generate_number_between),
            "jsonrpc", is_str(),
            "jsonrpc", is_("2.0"),
            "result", is_bool()
        )

        # Check authorization status
        lcc.set_step("Check that login successful")
        status = resp["result"]
        if status:
            lcc.log_info("Login successful")
        else:
            lcc.log_error("Login failed")


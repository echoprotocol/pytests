import json
import os

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_, is_integer, is_str
from websocket import create_connection

call_format = {"id": 0, "method": "call", "params": [{}, {}, {}]}  # id, method_name, data
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..//resources")
echo_dev = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
login_echo = json.load(open(os.path.join(RESOURCES_DIR, "echo_apis.json")))["LOGIN"]
database = json.load(open(os.path.join(RESOURCES_DIR, "echo_apis.json")))["DATABASE"]
get_block = json.load(open(os.path.join(RESOURCES_DIR, "database_methods.json")))["GET_BLOCK"]
get_transaction = json.load(open(os.path.join(RESOURCES_DIR, "database_methods.json")))["GET_TRANSACTIONS"]

SUITE = {
    "description": "Test 'ECHO'"
}


@lcc.suite("Simple test")
class TestEcho:
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

    def setup_suite(self):
        # Check status of connection
        if self.ws is not None:
            lcc.log_url(echo_dev)
            lcc.log_info("Connection successfully created")
        else:
            lcc.log_error("Connection not established")

        # Login to Echo
        lcc.set_step("Login to the Full Node")
        self.ws.send(json.dumps(self.call_method(login_echo)))

        # Receive authorization response
        resp = json.loads(self.ws.recv())
        lcc.log_info("Received: \n{}".format(json.dumps(resp, indent=4)))

    def teardown_suite(self):
        # Close connection to WebSocket
        lcc.set_step("Close connection")
        self.ws.close()
        lcc.log_info("Connection closed ")

    @lcc.test("Get response from database api")
    def test_get_response(self):
        # Authorization status check and request data from the database
        lcc.set_step("Requesting Access to an API")
        self.ws.send(json.dumps(self.call_method(database)))

        # Receive identifier
        resp = json.loads(self.ws.recv())
        lcc.log_info("Received: \n{}".format(json.dumps(resp, indent=4)))

        # Check the validity of the response from the server
        lcc.set_step("Check API response")
        self.check_resp_format(resp)

    @lcc.test("Get block")
    def test_get_block(self):
        # Get block
        lcc.set_step("Retrieve a full, signed block.")
        self.ws.send(json.dumps(self.call_method(get_block)))
        resp = json.loads(self.ws.recv())
        lcc.log_info("Received: \n{}".format(json.dumps(resp, indent=4)))

        # Check data in response
        lcc.set_step("Check API response")
        self.check_resp_format(resp)
        check_that_in(
            resp["result"],
            "previous", is_("0006e2288488b9fbcdb23f576a34b22869eae3e2")
        )

    @lcc.test("Get transaction")
    def test_get_transaction(self):
        # Get transaction
        lcc.set_step("Retrieve transaction.")
        self.ws.send(json.dumps(self.call_method(get_transaction)))
        resp = json.loads(self.ws.recv())
        lcc.log_info("Received: \n{}".format(json.dumps(resp, indent=4)))

        # Check data response
        lcc.set_step("Check API response")
        self.check_resp_format(resp)
        check_that_in(
            resp["result"],
            "ref_block_num", is_integer()
        )

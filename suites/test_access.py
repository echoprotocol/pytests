import json
import os

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_, is_integer
from websocket import create_connection

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

    def setup_suite(self):
        # Check status of connection
        if self.ws is not None:
            lcc.log_url(echo_dev)
            lcc.log_info("Connection successfully created")
        else:
            lcc.log_error("Connection not established")

        # Login to Echo
        lcc.set_step("Login to the Full Node")
        self.ws.send(json.dumps(login_echo))

        # Receive authorization response
        data = json.loads(self.ws.recv())
        lcc.log_info("Received: \n{}".format(json.dumps(data, indent=4)))

    def teardown_suite(self):
        # Close connection to WebSocket
        lcc.set_step("Close connection")
        self.ws.close()
        lcc.log_info("Connection closed ")

    @lcc.test("Get response from database api")
    def test_get_response(self, generate_number_between):
        # Authorization status check and request data from the database
        lcc.set_step("Requesting Access to an API")
        database["id"] = generate_number_between
        self.ws.send(json.dumps(database))

        # Receive identifier
        db = json.loads(self.ws.recv())
        lcc.log_info("Received: \n{}".format(json.dumps(db, indent=4)))

        # Check the validity of the response from the server
        lcc.set_step("Check API response")
        check_that_in(
            db,
            "id", is_(generate_number_between),
            "jsonrpc", is_("2.0"),
            "result", is_integer()
        )

    @lcc.test("Get block")
    def test_get_block(self, generate_number_between):
        # Get block
        lcc.set_step("Retrieve a full, signed block.")
        get_block["id"] = generate_number_between
        self.ws.send(json.dumps(get_block))
        block_info = json.loads(self.ws.recv())
        lcc.log_info("Received: \n{}".format(json.dumps(block_info, indent=4)))

        # Check data in response
        lcc.set_step("Check API response")
        check_that_in(
            block_info,
            "id", is_(generate_number_between),
            "jsonrpc", is_("2.0"),
        )
        check_that_in(
            block_info["result"],
            "previous", is_("0006e2288488b9fbcdb23f576a34b22869eae3e2")
        )

    @lcc.test("Get transaction")
    def test_get_transaction(self, generate_number_between):
        # Get transaction
        lcc.set_step("Retrieve transaction.")
        get_transaction["id"] = generate_number_between
        self.ws.send(json.dumps(get_transaction))
        transaction_info = json.loads(self.ws.recv())
        lcc.log_info("Received: \n{}".format(json.dumps(transaction_info, indent=4)))

        # Check data response
        lcc.set_step("Check API response")
        check_that_in(
            transaction_info,
            "id", is_(generate_number_between),
            "jsonrpc", is_("2.0"),
        )
        check_that_in(
            transaction_info["result"],
            "ref_block_num", is_integer()
        )

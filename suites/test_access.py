import json
import os

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_, is_integer

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..//resources")

SUITE = {
    "description": "Test 'ECHO'"
}


@lcc.suite("Simple test")
class TestEcho:
    def __init__(self):
        self.database = json.load(open(os.path.join(RESOURCES_DIR, "echo_apis.json")))["DATABASE"]

    @lcc.test("Get response from method")
    def test_get_response(self, connection, login, generate_number_between):
        # Authorization status check and request data from the database
        lcc.set_step("Requesting Access to an API")
        if login:
            self.database["id"] = generate_number_between
            connection.send(json.dumps(self.database))
        else:
            lcc.log_error("Login failed")

        # Receive identifier
        db = json.loads(connection.recv())
        lcc.log_info("Received: \n{}".format(json.dumps(db, indent=4)))

        # Check the validity of the response from the server
        lcc.set_step("Check API response")
        check_that_in(
            db,
            "id", is_(generate_number_between),
            "jsonrpc", is_("2.0"),
            "result", is_integer()
        )

        # Close connection to WebSocket
        lcc.set_step("Close connection")
        connection.close()
        lcc.log_info("Connection closed ")

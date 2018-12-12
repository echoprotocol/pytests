import json
import os

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_integer, is_, is_bool
from websocket import create_connection

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..//resources")
echo_dev = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
login_echo = json.load(open(os.path.join(RESOURCES_DIR, "echo_apis.json")))["LOGIN"]


@lcc.fixture(scope="suite")
def connection():
    """
    Connect to WebSocket
    :return: WebSocket
    """
    lcc.log_url(echo_dev)
    lcc.set_step("Create connection")
    ws = create_connection(echo_dev)
    lcc.log_info("Connection successfully created")
    return ws


@lcc.fixture()
def login(connection, generate_number_between):
    # Login to Echo
    lcc.set_step("Login to the Full Node")
    login_echo["id"] = generate_number_between
    connection.send(json.dumps(login_echo))

    # Receive authorization response
    data = json.loads(connection.recv())
    lcc.log_info("Received: \n{}".format(json.dumps(data, indent=4)))

    # Check the validity of the response from the server about authorization
    lcc.set_step("Check API response")
    check_that_in(
        data,
        "id", is_(generate_number_between),
        "jsonrpc", is_("2.0"),
        "result", is_bool()
    )

    # Authorization status check
    status = data["result"]
    if status:
        lcc.log_info("Login successful")
    else:
        lcc.log_warn("Login failed")
    return status

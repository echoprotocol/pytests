import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_bool
from common.utils import BaseTest

SUITE = {
    "description": "Test 'Login API'"
}


@lcc.suite("Test login method")
class TestLoginMethod(BaseTest):
    def __init__(self):
        super().__init__()
        self.login_data = "login_methods.json"
        self.login_empty_params = "LOGIN_EMPTY_PARAMS"
        self.login_valid_params = "LOGIN_VALID_PARAMS"
        self.database_api = "DATABASE"
        self.asset_api = "ASSET"
        self.history_api = "HISTORY"

    @lcc.test("Login with empty parameters")
    def test_login_with_empty_params(self):
        # Login to Echo
        self.send_request(self.get_data(self.login_data, self.login_empty_params))

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
        self.send_request(self.get_data(self.login_data, self.login_valid_params))

        # Receive authorization response
        resp = self.get_response()

        # Check response
        lcc.set_step("Check response with empty data")
        self.check_resp_format(resp)

        # Check authorization status
        lcc.set_step("Check that login successful")
        self.login_status(resp)

    @lcc.test("Connection to database api")
    def test_connection_to_db_api(self):
        # Login
        self.login_echo()

        # Authorization status check and request data from the database
        lcc.set_step("Requesting Access to an API")
        self.send_request(self.get_data(self.echo_api, self.database_api))

        # Receive identifier
        resp = self.get_response()

        # Check the validity of the response from the server
        lcc.set_step("Check API response")
        self.check_resp_format(resp)
        self.check_and_get_identifier(resp)

    @lcc.test("Connection to asset api")
    def test_connection_to_asset_api(self):
        # Login
        self.login_echo()

        # Authorization status check and request data from the asset api
        lcc.set_step("Requesting Access to an API")
        self.send_request(self.get_data(self.echo_api, self.asset_api))

        # Receive identifier
        resp = self.get_response()

        # Check the validity of the response from the server
        lcc.set_step("Check API response")
        self.check_resp_format(resp)
        self.check_and_get_identifier(resp)

    @lcc.test("Connection to history api")
    def test_connection_to_history_api(self):
        # Login
        self.login_echo()

        # Authorization status check and request data from the asset api
        lcc.set_step("Requesting Access to an API")
        self.send_request(self.get_data(self.echo_api, self.history_api))

        # Receive identifier
        resp = self.get_response()

        # Check the validity of the response from the server
        lcc.set_step("Check API response")
        self.check_resp_format(resp)
        self.check_and_get_identifier(resp)

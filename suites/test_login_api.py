import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_bool, equal_to
from common.utils import BaseTest

SUITE = {
    "description": "Test 'Login API'"
}


@lcc.suite("Test login methods")
class TestLoginMethod(BaseTest):
    login_valid_params = "login_valid_params"
    database_api = "database"
    asset_api = "asset"
    history_api = "history"

    def __init__(self):
        super().__init__()

    @lcc.test("Login with empty parameters")
    def test_login_with_empty_params(self):
        # Login to Echo
        self.send_request(self.get_request(self.login_api))

        # Receive authorization response
        resp = self.get_response()

        # Check response
        lcc.set_step("Check response with empty data")
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
        self.send_request(self.get_request(self.login_api, self.get_expected(self.login_valid_params)))

        # Receive authorization response
        resp = self.get_response()

        # Check response
        lcc.set_step("Check response with valid data")
        check_that_in(
            resp,
            "result", is_bool()
        )

        # Check authorization status
        lcc.set_step("Check that login successful")
        self.login_status(resp)

    @lcc.test("Connection to database api")
    def test_connection_to_db_api(self):
        # Authorization status check and request data from the database
        lcc.set_step("Requesting Access to an API")
        self.send_request(self.get_request(self.database_api))

        # Receive identifier
        resp = self.get_response()

        # Check the validity of the response from the server
        lcc.set_step("Check API response")
        check_that_in(resp, "result", equal_to(2))

    @lcc.test("Connection to asset api")
    def test_connection_to_asset_api(self):
        # Authorization status check and request data from the asset api
        lcc.set_step("Requesting Access to an API")
        self.send_request(self.get_request(self.asset_api))

        # Receive identifier
        resp = self.get_response()

        # Check the validity of the response from the server
        lcc.set_step("Check API response")
        check_that_in(resp, "result", equal_to(3))

    @lcc.test("Connection to history api")
    def test_connection_to_history_api(self):
        # Authorization status check and request data from the asset api
        lcc.set_step("Requesting Access to an API")
        self.send_request(self.get_request(self.history_api))

        # Receive identifier
        resp = self.get_response()

        # Check the validity of the response from the server
        lcc.set_step("Check API response")
        check_that_in(resp, "result", equal_to(4))

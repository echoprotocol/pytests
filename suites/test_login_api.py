import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_bool, equal_to, check_that
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
        check_that("'login status'", resp["result"], is_bool())

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
        check_that("'login status'", resp["result"], is_bool())

        # Check authorization status
        lcc.set_step("Check that login successful")
        self.login_status(resp)

    @lcc.test("Connection to database api")
    def test_connection_to_db_api(self):
        # Authorization to database api and get identifier
        lcc.set_step("Requesting Access to an Database API")
        resp = self.get_identifier(self.database_api)

        # Check database api identifier
        lcc.set_step("Check Database api identifier")
        check_that("'database api identifier'", resp, equal_to(2))

    @lcc.test("Connection to asset api")
    def test_connection_to_asset_api(self):
        # Authorization to asset api and get identifier
        lcc.set_step("Requesting Access to an Asset API")
        resp = self.get_identifier(self.asset_api)

        # Check asset api identifier
        lcc.set_step("Check Asset api identifier")
        check_that("'asset api identifier'", resp, equal_to(3))

    @lcc.test("Connection to history api")
    def test_connection_to_history_api(self):
        # Authorization to history api and get identifier
        lcc.set_step("Requesting Access to an History API")
        resp = self.get_identifier(self.history_api)

        # Check history api identifier
        lcc.set_step("Check History api identifier")
        check_that("'history api identifier'", resp, equal_to(4))

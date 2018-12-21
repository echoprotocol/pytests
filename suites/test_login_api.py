import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_bool, equal_to, check_that
from common.utils import BaseTest

SUITE = {
    "description": "Test 'Login API'"
}


@lcc.suite("Test login methods")
class TestLoginMethod(BaseTest):
    __login_valid_params = "login_valid_params"

    def __init__(self):
        super().__init__()
        self.__resp = None

    @lcc.test("Login with empty parameters")
    def test_login_with_empty_params(self):
        # Login to Echo
        self.send_request(self.get_request(self._login_api))

        # Receive authorization response
        self.__resp = self.get_response()

        # Check response
        lcc.set_step("Check response with empty data")
        check_that("'login status'", self.__resp["result"], is_bool())

        # Check authorization status
        lcc.set_step("Check that login successful")
        self.login_status(self.__resp)

    @lcc.test("Login with valid parameters")
    def test_login_with_valid_params(self):
        # Login to Echo
        lcc.set_step("Login to the Full Node with valid params")
        self.send_request(self.get_request(self._login_api, self.get_expected(self.__login_valid_params)))

        # Receive authorization response
        self.__resp = self.get_response()

        # Check response
        lcc.set_step("Check response with valid data")
        check_that("'login status'", self.__resp["result"], is_bool())

        # Check authorization status
        lcc.set_step("Check that login successful")
        self.login_status(self.__resp)

    @lcc.test("Connection to database api")
    def test_connection_to_db_api(self):
        # Authorization to database api and get identifier
        lcc.set_step("Requesting Access to an Database API")
        self.__resp = self.get_identifier(self._database_api)

        # Check database api identifier
        lcc.set_step("Check Database api identifier")
        check_that("'database api identifier'", self.__resp, equal_to(2))

    @lcc.test("Connection to asset api")
    def test_connection_to_asset_api(self):
        # Authorization to asset api and get identifier
        lcc.set_step("Requesting Access to an Asset API")
        self.__resp = self.get_identifier(self._asset_api)

        # Check asset api identifier
        lcc.set_step("Check Asset api identifier")
        check_that("'asset api identifier'", self.__resp, equal_to(3))

    @lcc.test("Connection to history api")
    def test_connection_to_history_api(self):
        # Authorization to history api and get identifier
        lcc.set_step("Requesting Access to an History API")
        self.__resp = self.get_identifier(self._history_api)

        # Check history api identifier
        lcc.set_step("Check History api identifier")
        check_that("'history api identifier'", self.__resp, equal_to(4))

    @lcc.test("Connection to network broadcast api")
    def test_connection_to_network_broadcast_api(self):
        # Authorization to network broadcast api and get identifier
        lcc.set_step("Requesting Access to an Network broadcast API")
        self.__resp = self.get_identifier(self._network_broadcast_api)

        # Check network broadcast api identifier
        lcc.set_step("Check Network broadcast api identifier")
        check_that("'network broadcast api identifier'", self.__resp, equal_to(5))

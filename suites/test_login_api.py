import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_bool
from common.utils import BaseTest

SUITE = {
    "description": "Test 'Login API'"
}


@lcc.suite("Test login method")
@lcc.disabled()
class TestLoginMethod(BaseTest):
    def __init__(self):
        super().__init__()
        self.login_data = "login_methods.json"
        self.login_empty_params = "LOGIN_EMPTY_PARAMS"
        self.login_valid_params = "LOGIN_VALID_PARAMS"

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

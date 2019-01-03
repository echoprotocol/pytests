import lemoncheesecake.api as lcc

from common.utils import BaseTest

SUITE = {
    "description": "Test 'Registration API'"
}


@lcc.suite("Test registration methods")
class TestRegistrationMethod(BaseTest):

    def __init__(self):
        super().__init__()
        self.__resp = None
        self.__identifier = self.get_identifier(self._registration_api)

    @lcc.test("Register an account")
    @lcc.disabled()
    def test_connection_to_registration_api(self):
        lcc.set_step("Register an account")
        register_account = ["test-n1",
                            "ECHO6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
                            "ECHO6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
                            "ECHO6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
                            "DETDvHDsAfk2M8LhYcxLZTbrNJRWT3UH5zxdaWimWc6uZkH"]
        self.send_request(self.get_request("register_account", register_account), self.__identifier)
        self.__resp = self.get_response()

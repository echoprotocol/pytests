# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from common.base_test import BaseTest

SUITE = {
    "description": "Check all the methods belonging to the registration_api"
}


@lcc.suite("Testing 'Registration API' methods call")
class RegistrationApi(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = self.get_identifier("registration")

    @lcc.test("Register an account")
    @lcc.disabled()
    def test_connection_to_registration_api(self):
        lcc.set_step("Register an account")
        register_account = ["test-n1",
                            "ECHO6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
                            "ECHO6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
                            "ECHO6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
                            "DETDvHDsAfk2M8LhYcxLZTbrNJRWT3UH5zxdaWimWc6uZkH"]
        response_id = self.send_request(self.get_request("register_account", register_account), self.__api_identifier)
        self.get_response(response_id)

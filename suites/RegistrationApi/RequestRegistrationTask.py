# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_integer, is_not

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'request_registration_task'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "notice", "registration_api", "request_registration_task")
@lcc.suite("Registration API", rank=1)
class RequestRegistrationTask(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))

    @lcc.tags("request_registration_task")
    @lcc.test("Simple work of method 'request_registration_task' ")
    def method_main_check(self):
        lcc.set_step("Call method 'request_registration_task'")
        response_id = self.send_request(self.get_request("request_registration_task"),
                                        self.__registration_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info("Get method response.")

        lcc.set_step("Check method response fields")
        if not self.type_validator.is_hex(result["block_id"]):
            lcc.log_error("Wrong format of 'block_id', got: '{}'".format(result["block_id"]))
        else:
            lcc.log_info("Block_id '{}' has correct format: hex".format(result["block_id"]))
        check_that("'rand_num not 0'", result["rand_num"], is_not(0))
        if not self.type_validator.is_digit(result["rand_num"]):
            lcc.log_error("Wrong format of 'rand_num', got: {}".format(result["rand_num"]))
        else:
            lcc.log_info("'rand_num' has correct format: int")
        check_that("difficulty", result["difficulty"], is_integer())

# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, require_that, has_length

from common.base_test import BaseTest
SUITE = {
    "description": "Method 'get_objects' (committee frozen balance object)"
}


@lcc.prop("main", "type")
@lcc.tags("api", "database_api", "database_api_objects", "get_objects")
@lcc.suite("Check work of method 'committee frozen balance object'", rank=1)
class GetCommitteeFrozenBalanceObject(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_objects' (committee frozen balance object)")
    def method_main_check(self):
        params = ['1.10.0']
        lcc.set_step("Get 'committee_frozen_balance' object")
        response_id = self.send_request(self.get_request("get_objects", [params]),
                                        self.__database_api_identifier)
        results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with params: {}".format(params))
        lcc.set_step("Check length of received objects")
        require_that(
            "'list of received objects'",
            results, has_length(len(params))
        )

        for i, committee_frozen_balance_info in enumerate(results):
            lcc.set_step("Checking 'committee_frozen_balance' object #{} - '{}'".format(i, params[i]))
            self.object_validator.validate_committee_frozen_balance_object(self, committee_frozen_balance_info)

            get_object_result = committee_frozen_balance_info["balance"]
            committee_member_id = committee_frozen_balance_info["owner"]
            lcc.set_step("Get 'committee_frozen_balance'")
            response_id = self.send_request(self.get_request("get_committee_frozen_balance", [committee_member_id]),
                                            self.__database_api_identifier)
            committee_frozen_balance_object_result = self.get_response(response_id)["result"]
            lcc.log_info("Call method 'get_committee_frozen_balance' with params: {}".format(committee_member_id))

            lcc.set_step("Check active committee member frozen balance")
            check_that("committee_frozen_balance", committee_frozen_balance_object_result, equal_to(get_object_result))

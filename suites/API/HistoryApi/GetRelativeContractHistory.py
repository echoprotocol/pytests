# -*- coding: utf-8 -*-

from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, check_that_in, has_length, is_integer, is_list

SUITE = {
    "description": "Method 'get_relative_contract_history'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "history_api", "get_relative_contract_history")
@lcc.suite("Check work of method 'get_relative_contract_history'", rank=1)
class GetRelativeContractHistory(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', "
            "history='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier, self.__history_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_relative_contract_history'")
    def method_main_check(self):
        stop, start = 0, 0
        limit = 1

        lcc.set_step("Perform create contract operation")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Get relative contract history")
        params = [contract_id, stop, limit, start]
        response_id = self.send_request(
            self.get_request("get_relative_contract_history", params), self.__history_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info(
            "Call method 'get_relative_contract_history' with: contract_id='{}', stop='{}', limit='{}', start='{}' "
            "parameters".format(contract_id, stop, limit, start)
        )

        lcc.set_step("Check response from method 'get_relative_contract_history'")
        results = response["result"]
        check_that("'number of history results'", results, has_length(limit))
        for result in results:
            if not self.type_validator.is_operation_history_id(result["id"]):
                lcc.log_error("Wrong format of 'operation id', got: {}".format(result["id"]))
            else:
                lcc.log_info("'operation_id' has correct format: operation_history_id")
            check_that_in(
                result,
                "op",
                is_list(),
                "result",
                is_list(),
                "block_num",
                is_integer(),
                "trx_in_block",
                is_integer(),
                "op_in_trx",
                is_integer(),
                "virtual_op",
                is_integer(),
                quiet=True
            )

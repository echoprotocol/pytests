# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, has_length, is_list, check_that_in, is_dict, check_that, \
    require_that_in, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Testing call uncorrect contract call"
}


@lcc.prop("main", "type")
@lcc.tags("scenarios", "call_uncorrect_contract")
@lcc.suite("Check scenario 'Testing call uncorrect contract call'")
class CallUncorrectContract(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("uncorrect_contract", "code")
        self.contract_func = self.get_byte_code("uncorrect_contract", "transfer()")

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

    @lcc.test("The scenario describes the mechanism of creating contract with not hex format of contract code")
    def call_uncorrect_contract(self):

        lcc.set_step("Create contract 'Uncorrect contract'")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier,
                                                 value_asset_id=self.echo_asset, supported_asset_id=self.echo_asset)

        lcc.set_step("Perform 'Uncorrect contract' contract call operation")
        broadcast_result = self.utils.perform_contract_call_operation(self, self.echo_acc0,
                                                                      method_bytecode=self.contract_func,
                                                                      database_api_id=self.__database_api_identifier,
                                                                      contract_id=contract_id)
        contract_result = self.get_operation_results_ids(broadcast_result)
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result]),
                                        self.__database_api_identifier)
        trx_completed_response = self.get_trx_completed_response(response_id)
        if require_that('contract call', trx_completed_response["result"], is_list()):
            check_that_in(
                trx_completed_response["result"][1],
                "exec_res", is_dict(),
                "tr_receipt", is_dict(),
                quiet=True
            )
            exec_res = trx_completed_response["result"][1]["exec_res"]
            check_that("exec_res", exec_res, has_length(6))
            tr_receipt = trx_completed_response["result"][1]["tr_receipt"]
            check_that("tr_receipt", tr_receipt, has_length(4))








# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, check_that_in, is_dict, has_length, require_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Testing contract calls with different asset ids (context)"
}

@lcc.disabled()
@lcc.prop("main", "type")
@lcc.tags("contract_context")
@lcc.suite("Check scenario 'Contract calls with different asset ids'")
class ContractsContext(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract_callee = self.get_byte_code("code_contract_Callee", "code")
        self.contract_caller = self.get_byte_code("code_contract_Caller", "code")
        self.func_call_callee = self.get_byte_code("code_contract_Caller", "call_Callee")
        self.func_call_callee_with_context = self.get_byte_code("code_contract_Caller", "call_Callee_with_context")

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
    def contract_context(self):
        lcc.set_step("Create contract 'Callee' with asset id: {}".format(self.echo_asset))
        self.utils.get_contract_id(self, self.echo_acc0, self.contract_callee,
                                   self.__database_api_identifier,
                                   value_asset_id=self.echo_asset,
                                   supported_asset_id=self.echo_asset)

        lcc.set_step("Create contract 'Callee' with asset id: {}".format(self.eth_asset))
        self.utils.get_contract_id(self, self.echo_acc0, self.contract_callee,
                                   self.__database_api_identifier,
                                   value_asset_id=self.eth_asset,
                                   supported_asset_id=self.eth_asset)

        lcc.set_step("Create contract 'Caller'")
        caller_contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_caller,
                                                        self.__database_api_identifier,
                                                        value_asset_id=self.eth_asset)

        lcc.set_step("Perform contact call operation with echo_asset_hex")
        echo_asset_id_hex = "0000000000000000000000000000000000000000000000000000000000000000"
        broadcast_result = self.utils.perform_contract_call_operation(self, self.echo_acc0,
                                                                      method_bytecode=(
                                                                              self.func_call_callee_with_context +
                                                                              echo_asset_id_hex),
                                                                      database_api_id=self.__database_api_identifier,
                                                                      contract_id=caller_contract_id)
        contract_result_id = self.get_operation_results_ids(broadcast_result)
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result_id]),
                                        self.__database_api_identifier)
        contract_result = self.get_trx_completed_response(response_id)["result"]
        if check_that("contract_result", contract_result[1], has_length(2)):
            check_that_in(
                contract_result[1],
                "exec_res", is_dict(),
                "tr_receipt", is_dict(),
                quiet=True
            )

        lcc.set_step("Perform contact call operation with eth_asset_hex")
        eth_asset_id_hex = "0000000000000000000000000000000000000000000000000000000000000001"
        broadcast_result = self.utils.perform_contract_call_operation(self, self.echo_acc0,
                                                                      method_bytecode=(
                                                                              self.func_call_callee_with_context +
                                                                              eth_asset_id_hex),
                                                                      database_api_id=self.__database_api_identifier,
                                                                      contract_id=caller_contract_id,
                                                                      value_asset_id=self.eth_asset)
        contract_result_id = self.get_operation_results_ids(broadcast_result)
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result_id]),
                                        self.__database_api_identifier)
        contract_result = self.get_trx_completed_response(response_id)["result"]
        if check_that("contract_result", contract_result[1], has_length(2)):
            check_that_in(
                contract_result[1],
                "exec_res", is_dict(),
                "tr_receipt", is_dict(),
                quiet=True
            )

        lcc.set_step("Perform call Callee contract")

        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.func_call_callee,
                                                              callee=caller_contract_id)
        response_id = self.send_request(self.get_request("get_required_fees", [[operation], self.echo_asset]),
                                        self.__database_api_identifier)
        response = \
            self.get_response(response_id, negative=True)["error"]["data"]["stack"][0]["data"]["e"]["excepted"]
        error_massage = "InvalidAssetType"
        require_that("'error massage'", response, equal_to(error_massage))

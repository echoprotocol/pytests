# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from common.base_test import BaseTest

SUITE = {
    "description": "Testing contract calls with different asset ids (context)"
}


@lcc.prop("main", "type")
@lcc.tags("scenarios", "contract_context")
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
                                   supported_asset_id=self.echo_asset,
                                   log_broadcast=True)

        lcc.set_step("Create contract 'Callee' with asset id: {}".format(self.eth_asset))
        self.utils.get_contract_id(self, self.echo_acc0, self.contract_callee,
                                   self.__database_api_identifier,
                                   value_asset_id=self.eth_asset,
                                   supported_asset_id=self.eth_asset,
                                   log_broadcast=True)

        lcc.set_step("Create contract 'Caller'")
        caller_contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_caller,
                                                        self.__database_api_identifier,
                                                        value_asset_id=self.eth_asset,
                                                        log_broadcast=True)

        lcc.set_step("Perform operations using a new account. caller_contract contract operation count equal to limit")
        broadcast_result = self.utils.perform_contract_call_operation(self, self.echo_acc0,
                                                                      method_bytecode=(
                                                                                  self.func_call_callee),
                                                                      database_api_id=self.__database_api_identifier,
                                                                      contract_id=caller_contract_id,
                                                                      log_broadcast=True)
        contract_result = self.get_operation_results_ids(broadcast_result)
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result]),
                                        self.__database_api_identifier)
        contract_id_16 = self.get_trx_completed_response(response_id, debug_mode=True)

        lcc.set_step("Perform operations using a new account. caller_contract contract operation count equal to limit")
        asset_id_hex = "0000000000000000000000000000000000000000000000000000000000000000"
        broadcast_result = self.utils.perform_contract_call_operation(self, self.echo_acc0,
                                                                      method_bytecode=(
                                                                                  self.func_call_callee_with_context + asset_id_hex),
                                                                      database_api_id=self.__database_api_identifier,
                                                                      contract_id=caller_contract_id,
                                                                      log_broadcast=True)
        contract_result = self.get_operation_results_ids(broadcast_result)
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result]),
                                        self.__database_api_identifier)
        contract_id_16 = self.get_trx_completed_response(response_id, debug_mode=True)

        lcc.set_step("Perform operations using a new account. caller_contract contract operation count equal to limit")
        asset_id_hex = "0000000000000000000000000000000000000000000000000000000000000001"
        broadcast_result = self.utils.perform_contract_call_operation(self, self.echo_acc0,
                                                                      method_bytecode=(
                                                                                  self.func_call_callee + asset_id_hex),
                                                                      database_api_id=self.__database_api_identifier,
                                                                      contract_id=caller_contract_id
                                                                      ,
                                                                      log_broadcast=True)
        contract_result = self.get_operation_results_ids(broadcast_result)
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result]),
                                        self.__database_api_identifier)
        contract_id_16 = self.get_trx_completed_response(response_id, debug_mode=True)

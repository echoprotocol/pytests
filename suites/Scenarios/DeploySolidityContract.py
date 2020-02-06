# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from common.base_test import BaseTest

SUITE = {
    "description": "Testing solidity 0.6 contract call"
}

# todo: Undisabled when ECHO-1750 will be done
@lcc.disabled()
@lcc.prop("main", "type")
@lcc.tags("scenarios", "deploy_solidity_contract")
@lcc.suite("Check scenario 'deploy_solidity_contract'")
class DeploySolidityContract(BaseTest):
    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("solidity_contract", "code")
        self.method = self.get_byte_code("solidity_contract", "code")
        self.value_amount = 10

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

    @lcc.test("The scenario describes behavior of solidity contact call.")
    def wrong_contract_call(self):

        lcc.set_step("Create 'Solidity 0.6 contract' contract in the Echo network")
        operation = self.echo_ops.get_contract_create_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                bytecode=self.contract,
                                                                value_asset_id=self.echo_asset)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier, fee_amount=200)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=True)
        contract_id = \
            self.get_contract_result(broadcast_result, self.__database_api_identifier, mode="evm")["result"][1][
                "contract_id"]
        lcc.log_info("Created contract id: {}".format(contract_id))

        # todo: Added contract method call
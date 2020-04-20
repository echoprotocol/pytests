# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc

from common.base_test import BaseTest

SUITE = {
    "description": "Testing correct work of contract with 'eth_accuracy:True'"
}

@lcc.tags("Manual testing")
@lcc.disabled()
@lcc.prop("main", "type")
@lcc.tags("scenarios", "eth_accuracy")
@lcc.suite("Check scenario 'eth_accuracy'")
class EthAccuracy(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("eth_accuracy", "code")
        self.balance = self.get_byte_code("eth_accuracy", "balance()")
        self.withdraw = self.get_byte_code("eth_accuracy", "withdraw(address,uint256)")

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', "
            "history='{}'".format(self.__database_api_identifier, self.__registration_api_identifier,
                                  self.__history_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}' '{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("The scenario describes the work of contract with 'eth_accuracy:True'")
    def eth_accuracy(self):
        echo_accuracy_amount = 1
        contract_ids = []
        withdraw_amount = 1

        for i in ["one", "two"]:
            lcc.set_step("Create contract in the Echo network and get its contract id")
            contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract,
                                                     self.__database_api_identifier, eth_accuracy=True,
                                                     log_broadcast=True)
            lcc.log_info("contract id: {}".format(contract_id))
            contract_ids.append(contract_id)

            response_id = self.send_request(
                self.get_request("get_account_balances", [self.echo_acc0, [self.echo_asset]]),
                self.__database_api_identifier)
            total_balance = self.get_response(response_id, log_response=True)

            lcc.set_step(
                "Call 'payable' method = add {} assets to contact {}".format(echo_accuracy_amount, contract_id))
            operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                  bytecode="", callee=contract_id,
                                                                  value_amount=echo_accuracy_amount)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                       log_broadcast=True)

            lcc.set_step("Call 'balanceof()' method = Get contact {} balance".format(contract_id))
            operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                  bytecode=self.balance, callee=contract_id)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                       log_broadcast=True)
            contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
            contract_output = self.get_contract_output(contract_result, output_type=int)
            lcc.log_info("contract_output: {}".format(contract_output))

        response_id = self.send_request(self.get_request("get_account_balances", [self.echo_acc1, [self.echo_asset]]),
                                        self.__database_api_identifier)
        total_balance = self.get_response(response_id, log_response=True)

        lcc.set_step("Call 'withdraw()' method with {} amount".format(withdraw_amount))
        bytecode = (str(self.withdraw) + "000000000000000000000000000000000000000000000000000000000000000d0000000000000000000000000000000000000000000000000000000005F5E100")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              value_amount=0, bytecode=bytecode,
                                                              callee=contract_ids[0])
        collected_operation = self.collect_operations(operation, self.__database_api_identifier, fee_amount=200, debug_mode=True)
        lcc.log_debug(str(collected_operation))
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=operation,
                                                   log_broadcast=True)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))

        self.produce_block(self.__database_api_identifier)
        #
        response_id = self.send_request(self.get_request("get_account_balances", [self.echo_acc1, ["1.3.0"]]),
                                        self.__database_api_identifier, debug_mode=True)
        total_balance = self.get_response(response_id, log_response=True)

        lcc.set_step("Call 'balanceof()' method = Get contact {} balance".format(contract_id))
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.balance,
                                                              callee=contract_ids[0])
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_output = self.get_contract_output(contract_result, output_type=int)
        lcc.log_info("contract_output: {}".format(contract_output))

        lcc.set_step("Call 'balanceof()' method = Get contact {} balance".format(contract_id))
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.balance,
                                                              callee=contract_ids[1])
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        # lcc.log_info("contract result: {}".format(contract_result))
        contract_output = self.get_contract_output(contract_result, output_type=int)
        lcc.log_info("contract_output: {}".format(contract_output))

        # response_id = self.send_request(self.get_request("get_contract_result", ["1.12.98"]),
        #                                 self.__database_api_identifier)
        # result = self.get_response(response_id, log_response=True)

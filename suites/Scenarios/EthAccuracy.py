# -*- coding: utf-8 -*-

from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Testing correct work of contract with 'eth_accuracy:True'"
}


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
            "history='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier, self.__history_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        self.echo_acc1 = self.get_account_id(
            self.accounts[1], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account is '{}' '{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("The scenario describes the work of contract with 'eth_accuracy:True'")
    def eth_accuracy(self):
        echo_accuracy_amount = 1
        contract_ids = []
        withdraw_amount = 1
        eth_accuracy_balance = 10000000000

        for i in range(2):
            lcc.set_step("Create contract in the Echo network and get its contract id")
            contract_id = self.utils.get_contract_id(
                self,
                self.echo_acc0,
                self.contract,
                self.__database_api_identifier,
                eth_accuracy=True,
                log_broadcast=False
            )
            lcc.log_info("contract id: {}".format(contract_id))
            contract_ids.append(contract_id)

            lcc.set_step(
                "Call 'payable' method = add {} assets to contact {}".format(echo_accuracy_amount, contract_id)
            )
            operation = self.echo_ops.get_contract_call_operation(
                echo=self.echo,
                registrar=self.echo_acc0,
                bytecode="",
                callee=contract_id,
                value_amount=echo_accuracy_amount
            )
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)

            lcc.set_step("Call 'balanceof()' method = Get contact {} balance".format(contract_id))
            operation = self.echo_ops.get_contract_call_operation(
                echo=self.echo, registrar=self.echo_acc0, bytecode=self.balance, callee=contract_id
            )
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(
                echo=self.echo, list_operations=collected_operation, log_broadcast=False
            )
            contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
            contract_output = self.get_contract_output(contract_result, output_type=int)
            lcc.log_info("contract_output: {}".format(contract_output))

        lcc.set_step("Call 'balanceof()' method = Get contact {} balance".format(contract_id[0]))
        operation = self.echo_ops.get_contract_call_operation(
            echo=self.echo, registrar=self.echo_acc0, bytecode=self.balance, callee=contract_ids[0]
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_output = self.get_contract_output(contract_result, output_type=int)
        check_that("contract balance", contract_output, equal_to(eth_accuracy_balance))

        lcc.set_step("Call 'balanceof()' method = Get contact {} balance".format(contract_id[1]))
        operation = self.echo_ops.get_contract_call_operation(
            echo=self.echo, registrar=self.echo_acc0, bytecode=self.balance, callee=contract_ids[1]
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_output = self.get_contract_output(contract_result, output_type=int)
        check_that("contract balance", contract_output, equal_to(eth_accuracy_balance))

        lcc.set_step(
            "Call 'withdraw()' to contract address method with {} amount of contract {}".format(
                withdraw_amount, contract_ids[0]
            )
        )
        contract_id_hex = hex(int(contract_ids[1].split(".")[-1])).split("x")[-1]
        bytecode = (
            '{}{}{}{}'.format(
                str(self.withdraw), "00000000000000000000000001000000000000000000000000000000000000", contract_id_hex,
                "00000000000000000000000000000000000000000000000000000002540BE400"
            )
        )
        operation = self.echo_ops.get_contract_call_operation(
            echo=self.echo, registrar=self.echo_acc0, value_amount=0, bytecode=bytecode, callee=contract_ids[0]
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier, fee_amount=200)
        broadcast_result = self.echo_ops.broadcast(
            echo=self.echo, list_operations=collected_operation, log_broadcast=False
        )
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        lcc.log_info(" {}".format(contract_result))
        self.produce_block(self.__database_api_identifier)

        lcc.set_step("Get contact {} balance after withdrawal to contract address".format(contract_ids[1]))
        operation = self.echo_ops.get_contract_call_operation(
            echo=self.echo, registrar=self.echo_acc0, bytecode=self.balance, callee=contract_ids[1]
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_output = self.get_contract_output(contract_result, output_type=int)
        check_that("contract balance", contract_output, equal_to(eth_accuracy_balance * 2))

        lcc.set_step("Get contact {} balance after withdrawal to contract address".format(contract_ids[0]))
        operation = self.echo_ops.get_contract_call_operation(
            echo=self.echo, registrar=self.echo_acc0, bytecode=self.balance, callee=contract_ids[0]
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_output = self.get_contract_output(contract_result, output_type=int)
        check_that("contract balance", contract_output, equal_to(0))

        lcc.set_step("Get balances of '1.2.6' account before withdrawal")
        params = ["1.2.9", ["1.3.0"]]
        response_id = self.send_request(
            self.get_request("get_account_balances", params), self.__database_api_identifier
        )
        balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("Balance is {}".format(balance))

        lcc.set_step(
            "Call 'withdraw()' to '1.2.6' account address method with {} amount of contract {}".format(
                withdraw_amount, contract_ids[1]
            )
        )
        bytecode = (
            '{}{}'.format(
                str(self.withdraw),
                "000000000000000000000000000000000000000000000000000000000000000900000000000000000000000000000000000000000000000000000002540BE400"
            )
        )
        operation = self.echo_ops.get_contract_call_operation(
            echo=self.echo, registrar=self.echo_acc0, value_amount=0, bytecode=bytecode, callee=contract_ids[1]
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier, fee_amount=200)
        broadcast_result = self.echo_ops.broadcast(
            echo=self.echo, list_operations=collected_operation, log_broadcast=False
        )
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        lcc.log_info(" {}".format(contract_result))
        self.produce_block(self.__database_api_identifier)

        lcc.set_step("Get contact {} balance after withdrawal to account address".format(contract_ids[1]))
        operation = self.echo_ops.get_contract_call_operation(
            echo=self.echo, registrar=self.echo_acc0, bytecode=self.balance, callee=contract_ids[1]
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_output = self.get_contract_output(contract_result, output_type=int)
        check_that("contract balance", contract_output, equal_to(eth_accuracy_balance))

        lcc.set_step("Get balances of '1.2.6' account after withdrawal")
        params = ["1.2.9", ["1.3.0"]]
        response_id = self.send_request(
            self.get_request("get_account_balances", params), self.__database_api_identifier
        )
        updated_balance = self.get_response(response_id)["result"][0]["amount"]
        check_that("contract balance", int(updated_balance), equal_to(int(balance) + 1))

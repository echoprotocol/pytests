# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_, check_that_in, greater_than_or_equal_to, is_true, is_list, \
    has_length, check_that, equal_to, starts_with

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_withdrawals'"
}


@lcc.prop("main", "type")
@lcc.tags(
    "api", "database_api", "sidechain", "sidechain_ethereum",
    "database_api_sidechain_ethereum", "get_account_withdrawals"
)
@lcc.suite("Check work of method 'get_account_withdrawals'", rank=1)
class GetAccountWithdrawals(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.eth_address = None
        self.echo_acc0 = None

    @staticmethod
    def get_random_amount(_to, _from=0.01):
        return round(random.uniform(_from, _to))

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_ethereum()
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
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        self.eth_address = self.get_default_ethereum_account().address
        lcc.log_info("Ethereum address in the ethereum network: '{}'".format(self.eth_address))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_account_withdrawals'")
    def method_main_check(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        eth_amount = 0.01
        withdraw_ids = []
        withdraw_values = []
        sidechain_eth_burn_operations = []

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_sidechain_eth_create_address_operation(self, new_account, self.__database_api_identifier)
        lcc.log_info("Ethereum address generated successfully")

        lcc.set_step("Get ethereum address of created account in the network")
        eth_account_address = self.utils.get_eth_address(self, new_account,
                                                         self.__database_api_identifier)["result"]["eth_addr"]
        lcc.log_info("Ethereum address of '{}' account is '{}'".format(new_account, eth_account_address))

        lcc.set_step("Get unpaid fee for ethereum address creation")
        unpaid_fee_in_ethereum = self.eth_trx.get_unpaid_fee(self, self.web3, new_account)
        lcc.log_info("Unpaid fee for creation ethereum address for '{}' account: '{}'".format(new_account,
                                                                                              unpaid_fee_in_ethereum))

        lcc.set_step("Send eth to ethereum address of created account")
        transaction = self.eth_trx.get_transfer_transaction(web3=self.web3, _from=self.eth_address,
                                                            _to=eth_account_address,
                                                            value=eth_amount + unpaid_fee_in_ethereum)
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)

        lcc.set_step("Get account balance in ethereum")
        ethereum_balance = self.utils.get_eth_balance(self, new_account, self.__database_api_identifier)
        lcc.log_info("Account '{}' balance in ethereum is '{}'".format(new_account, ethereum_balance))

        lcc.set_step("First withdraw eth from ECHO network to Ethereum network")
        withdraw_amount = self.get_random_amount(_to=int(ethereum_balance))
        withdraw_values.append(withdraw_amount)
        self.utils.perform_sidechain_eth_withdraw_operation(self, new_account, self.eth_address, withdraw_amount,
                                                            self.__database_api_identifier)
        lcc.log_info("Withdraw '{}' eeth from '{}' account".format(withdraw_amount, new_account))

        lcc.set_step("Store the first withdraw operation EchoToEth")
        sidechain_eth_burn_operation = self.echo_ops.get_operation_json("sidechain_eth_burn_operation", example=True)
        sidechain_eth_burn_operation[1]["value"].update({"amount": withdraw_values[0]})
        sidechain_eth_burn_operation[1].update({"account": new_account})
        sidechain_eth_burn_operations.insert(0, sidechain_eth_burn_operation)
        lcc.log_info("First withdraw operation stored")

        lcc.set_step("Get account history operations")
        operation_id = self.echo.config.operation_ids.SIDECHAIN_ETH_BURN
        results = self.utils.get_account_history_operations(self, new_account, operation_id,
                                                            self.__history_api_identifier,
                                                            self.__database_api_identifier,
                                                            limit=len(sidechain_eth_burn_operations))["result"]
        lcc.log_info("Account history operations of 'sidechain_eth_burn_operation' received")

        lcc.set_step("Check response from method 'get_account_history_operations'")
        for i, result in enumerate(results):
            operation_in_history = result["op"]
            lcc.set_step("Check operation #{} in account history operations".format(i))
            check_that("operation_id", operation_in_history[0], equal_to(operation_id))
            check_that_in(
                operation_in_history[1],
                "fee", equal_to(sidechain_eth_burn_operations[i][1]["fee"]),
                "account", equal_to(sidechain_eth_burn_operations[i][1]["account"]),
                "withdraw_id", starts_with(self.get_object_type(self.echo.config.object_types.WITHDRAW_ETH))
            )
            self.check_uint256_numbers(operation_in_history[1]["value"], "amount")
            check_that_in(
                operation_in_history[1]["value"],
                "asset_id", equal_to(sidechain_eth_burn_operations[i][1]["value"]["asset_id"])
            )

        lcc.set_step("Get updated account balance in ethereum after first withdraw")
        ethereum_balance = self.utils.get_eth_balance(self, new_account, self.__database_api_identifier,
                                                      previous_balance=ethereum_balance)
        lcc.log_info("Account '{}' updated balance in ethereum is '{}'".format(new_account, ethereum_balance))

        lcc.set_step("Second withdraw eth from ECHO network to Ethereum network")
        withdraw_amount = self.get_random_amount(_to=int(ethereum_balance))
        withdraw_values.append(withdraw_amount)
        self.utils.perform_sidechain_eth_withdraw_operation(self, new_account, self.eth_address, withdraw_amount,
                                                            self.__database_api_identifier)
        lcc.log_info("Withdraw '{}' eeth from '{}' account".format(withdraw_amount, new_account))

        lcc.set_step("Store the second withdraw operation EchoToEth")
        sidechain_eth_burn_operation = self.echo_ops.get_operation_json("sidechain_eth_burn_operation", example=True)
        sidechain_eth_burn_operation[1]["value"].update({"amount": withdraw_values[1]})
        sidechain_eth_burn_operation[1].update({"account": new_account})
        sidechain_eth_burn_operations.insert(0, sidechain_eth_burn_operation)
        lcc.log_info("Second withdraw operation stored")

        lcc.set_step("Get account history operations")
        operation_id = self.echo.config.operation_ids.SIDECHAIN_ETH_BURN
        results = self.utils.get_account_history_operations(self, new_account, operation_id,
                                                            self.__history_api_identifier,
                                                            self.__database_api_identifier,
                                                            limit=len(sidechain_eth_burn_operations))["result"]
        lcc.log_info("Account history operations of 'sidechain_eth_burn_operation' received")

        lcc.set_step("Check response from method 'get_account_history_operations'")
        for i, result in enumerate(results):
            operation_in_history = result["op"]
            lcc.set_step("Check operation #{} in account history operations".format(i))
            check_that("operation_id", operation_in_history[0], equal_to(operation_id))
            check_that_in(
                operation_in_history[1],
                "fee", equal_to(sidechain_eth_burn_operations[i][1]["fee"]),
                "account", equal_to(sidechain_eth_burn_operations[i][1]["account"]),
                "withdraw_id", starts_with(self.get_object_type(self.echo.config.object_types.WITHDRAW_ETH))
            )
            self.check_uint256_numbers(operation_in_history[1]["value"], "amount")
            check_that_in(
                operation_in_history[1]["value"],
                "asset_id", equal_to(sidechain_eth_burn_operations[i][1]["value"]["asset_id"])
            )

        lcc.set_step("Get withdrawals of created account")
        params = [new_account]
        response_id = self.send_request(self.get_request("get_account_withdrawals", params),
                                        self.__database_api_identifier)
        withdrawals = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_account_withdrawals' of new account '{}'".format(new_account))

        lcc.set_step("Check simple work of method 'get_account_withdrawals'")
        for i, withdraw in enumerate(withdrawals):
            lcc.set_step("Check account withdraw #{}".format(i))
            require_that(
                "'first deposit of created account'",
                withdraw, has_length(8)
            )
            if not self.validator.is_withdraw_eth_id(withdraw["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(withdraw["id"]))
            else:
                lcc.log_info("'id' has correct format: withdraw_eth_object_type")
            if not self.validator.is_eth_address(withdraw["eth_addr"]):
                lcc.log_error("Wrong format of 'eth_addr', got: {}".format(withdraw["eth_addr"]))
            else:
                lcc.log_info("'eth_addr' has correct format: ethereum_address_type")
            withdraw_ids.append(withdraw["id"])
            check_that_in(
                withdraw,
                "withdraw_id", greater_than_or_equal_to(0),
                "account", is_(new_account),
                "is_approved", is_true(),
                "approves", is_list(),
                "extensions", is_list(),
            )
            check_that("value", int(withdraw["value"]), is_(withdraw_values[i]), quiet=True)

        lcc.set_step("Get withdraw by id using 'get_objects'")
        response_id = self.send_request(self.get_request("get_objects", [withdraw_ids]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with param: {}".format(withdraw_ids))

        lcc.set_step("Compare withdrawals in 'get_account_withdrawals' with method 'get_objects'")
        for i, withdraw in enumerate(withdrawals):
            lcc.set_step("Compare #{}, withdraw in 'get_account_withdrawals' with method 'get_objects'".format(i))
            check_that_in(
                withdraw,
                "id", is_(response[i]["id"]),
                "withdraw_id", is_(response[i]["withdraw_id"]),
                "account", is_(response[i]["account"]),
                "eth_addr", is_(response[i]["eth_addr"]),
                "value", is_(response[i]["value"]),
                "is_approved", is_(response[i]["is_approved"]),
                "approves", is_(response[i]["approves"]),
                "extensions", is_(response[i]["extensions"]),
                quiet=True
            )

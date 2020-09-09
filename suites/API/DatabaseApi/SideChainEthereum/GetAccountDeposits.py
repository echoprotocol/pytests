# -*- coding: utf-8 -*-
import random

from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import (
    check_that, check_that_in, equal_to, has_length, is_, is_true, require_that, require_that_in, starts_with
)

SUITE = {
    "description": "Methods 'get_account_deposits', 'get_objects' (deposit eth object)"
}


@lcc.prop("main", "type")
@lcc.tags(
    "api", "database_api", "sidechain", "sidechain_ethereum", "database_api_sidechain_ethereum", "get_account_deposits",
    "database_api_objects", "get_objects"
)
@lcc.suite("Check work of methods: 'get_account_deposits', 'get_objects' (deposit eth object)", rank=1)
class GetAccountDeposits(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.echo_acc0 = None
        self.eth_address = None

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
            "history='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier, self.__history_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        self.eth_address = self.get_default_ethereum_account().address
        lcc.log_info("Ethereum address in the ethereum network: '{}'".format(self.eth_address))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of methods 'get_account_deposits', 'get_objects' (deposit eth object)")
    def method_main_check(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        eth_amount = 0.01
        deposit_ids = []
        deposit_values = []
        sidechain_issue_operations = []

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(
            new_account, self.__database_api_identifier, self.__registration_api_identifier
        )
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
        lcc.log_info(
            "Unpaid fee for creation ethereum address for '{}' account: '{}'".format(
                new_account, unpaid_fee_in_ethereum
            )
        )

        lcc.set_step("First send eth to ethereum address of created account")
        transaction = self.eth_trx.get_transfer_transaction(
            web3=self.web3, _from=self.eth_address, _to=eth_account_address, value=eth_amount + unpaid_fee_in_ethereum
        )
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)
        deposit_values.append(self.utils.convert_ethereum_to_eeth(eth_amount))

        lcc.set_step("Store the first sent operation EthToEcho")
        sidechain_issue_operation = self.echo_ops.get_operation_json("sidechain_issue_operation", example=True)
        sidechain_issue_operation[1]["value"].update({"amount": deposit_values[0]})
        sidechain_issue_operation[1].update({"account": new_account})
        sidechain_issue_operations.insert(0, sidechain_issue_operation)
        lcc.log_info("First deposit operation stored")

        lcc.set_step("Get account history operations")
        operation_id = self.echo.config.operation_ids.SIDECHAIN_ISSUE
        results = self.utils.get_account_history_operations(
            self,
            new_account,
            operation_id,
            self.__history_api_identifier,
            self.__database_api_identifier,
            limit=len(sidechain_issue_operations)
        )["result"]
        lcc.log_info("Account history operations of 'sidechain_issue_operation' received")

        lcc.set_step("Check response from method 'get_account_history_operations'")
        for i, result in enumerate(results):
            operation_in_history = result["op"]
            lcc.set_step("Check operation #{} in account history operations".format(i))
            check_that("operation_id", operation_in_history[0], equal_to(operation_id), quiet=True)
            check_that_in(
                operation_in_history[1],
                "fee",
                equal_to(sidechain_issue_operations[i][1]["fee"]),
                "account",
                equal_to(sidechain_issue_operations[i][1]["account"]),
                "deposit_id",
                starts_with(self.get_object_type(self.echo.config.object_types.ETH_DEPOSIT)),
                quiet=True
            )
            self.check_uint256_numbers(operation_in_history[1]["value"], "amount", quiet=True)
            check_that_in(
                operation_in_history[1]["value"],
                "asset_id",
                equal_to(sidechain_issue_operations[i][1]["value"]["asset_id"]),
                quiet=True
            )

        lcc.set_step("Second send eth to ethereum address of created account")
        eth_amount = eth_amount + eth_amount
        transaction = self.eth_trx.get_transfer_transaction(
            web3=self.web3, _from=self.eth_address, _to=eth_account_address, value=eth_amount
        )
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)
        deposit_values.append(self.utils.convert_ethereum_to_eeth(eth_amount))

        lcc.set_step("Store the second sent operation EthToEcho")
        sidechain_issue_operation = self.echo_ops.get_operation_json("sidechain_issue_operation", example=True)
        sidechain_issue_operation[1]["value"].update({"amount": deposit_values[1]})
        sidechain_issue_operation[1].update({"account": new_account})
        sidechain_issue_operations.insert(0, sidechain_issue_operation)
        lcc.log_info("Second deposit operation stored")

        lcc.set_step("Get account history operations")
        operation_id = self.echo.config.operation_ids.SIDECHAIN_ISSUE
        results = self.utils.get_account_history_operations(
            self,
            new_account,
            operation_id,
            self.__history_api_identifier,
            self.__database_api_identifier,
            limit=len(sidechain_issue_operations)
        )["result"]
        lcc.log_info("Account history operations of 'sidechain_issue_operation' received")

        lcc.set_step("Check response from method 'get_account_history_operations'")
        for i, result in enumerate(results):
            operation_in_history = result["op"]
            lcc.set_step("Check operation #{} in account history operations".format(i))
            check_that("operation_id", operation_in_history[0], equal_to(operation_id), quiet=True)
            check_that_in(
                operation_in_history[1],
                "fee",
                equal_to(sidechain_issue_operations[i][1]["fee"]),
                "account",
                equal_to(sidechain_issue_operations[i][1]["account"]),
                "deposit_id",
                starts_with(self.get_object_type(self.echo.config.object_types.ETH_DEPOSIT)),
                quiet=True
            )
            self.check_uint256_numbers(operation_in_history[1]["value"], "amount", quiet=True)
            check_that_in(
                operation_in_history[1]["value"],
                "asset_id",
                equal_to(sidechain_issue_operations[i][1]["value"]["asset_id"]),
                quiet=True
            )

        lcc.set_step("Get deposits of created account")
        params = [new_account, "eth"]
        response_id = self.send_request(
            self.get_request("get_account_deposits", params), self.__database_api_identifier
        )
        get_account_deposits_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_account_deposits' of new account '{}'".format(new_account))

        lcc.set_step("Check simple work of method 'get_account_deposits'")
        for i, deposit in enumerate(get_account_deposits_results):
            lcc.set_step("Check account deposit #{}".format(i))
            self.object_validator.validate_deposit_eth_object(self, deposit)
            deposit_ids.append(deposit["id"])
            require_that_in(
                deposit,
                "account",
                is_(new_account),
                "is_approved",
                is_true(),
                "value",
                is_(deposit_values[i]),
                quiet=True
            )

        lcc.set_step("Get deposit by id using 'get_objects'")
        params = deposit_ids
        response_id = self.send_request(self.get_request("get_objects", [params]), self.__database_api_identifier)
        get_objects_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with param: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that("'list of received objects'", get_objects_results, has_length(len(params)), quiet=True)

        lcc.set_step("Compare deposits in 'get_account_deposits' with method 'get_objects'")
        for i, deposit in enumerate(get_account_deposits_results):
            lcc.set_step("Compare #{}: deposit in 'get_account_deposits' with method 'get_objects'".format(i))
            require_that("result", get_objects_results[i], equal_to(deposit), quiet=True)

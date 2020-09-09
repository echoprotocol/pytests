# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, has_item

SUITE = {
    "description": "Operation 'contract_whitelist'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "contract_operations", "contract_whitelist")
@lcc.suite("Check work of method 'contract_whitelist'", rank=1)
class ContractWhitelist(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.echo_acc0 = None
        self.echo_acc1 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        self.echo_acc1 = self.get_account_id(
            self.accounts[1], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'contract_whitelist'")
    def method_main_check(self, get_random_integer_up_to_ten):
        value_amount = get_random_integer_up_to_ten
        lcc.set_step("Create 'Piggy' contract")
        operation = self.echo_ops.get_contract_create_operation(
            echo=self.echo,
            registrar=self.echo_acc0,
            bytecode=self.piggy_contract,
            value_amount=value_amount,
            value_asset_id=self.echo_asset
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_id = self.get_contract_id(contract_result)

        lcc.set_step("Perform 'contract_fund_pool' operation")
        operation = self.echo_ops.get_contract_fund_pool_operation(
            echo=self.echo, sender=self.echo_acc0, contract=contract_id, value_amount=value_amount
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("'contract_fund_pool' broadcasted successfully")

        lcc.set_step("Get 'contract_pool_balance'")
        response_id = self.send_request(
            self.get_request("get_contract_pool_balance", [contract_id]), self.__database_api_identifier
        )
        amount = self.get_response(response_id)["result"]["amount"]
        lcc.log_info("'contract_fund_pool' added, amount: '{}'".format(amount))

        lcc.set_step("Add accounts to whitelist and blacklist and check that accounts where added")
        contract_whitelist_operation = self.echo_ops.get_contract_whitelist_operation(
            echo=self.echo,
            sender=self.echo_acc0,
            contract=contract_id,
            add_to_whitelist=[self.echo_acc1],
            add_to_blacklist=[self.echo_acc0]
        )
        collected_contract_whitelist = self.collect_operations(
            contract_whitelist_operation, self.__database_api_identifier
        )
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_contract_whitelist)
        response_id = self.send_request(
            self.get_request("get_contract_pool_whitelist", [contract_id]), self.__database_api_identifier
        )
        result = self.get_response(response_id)["result"]
        check_that("contract whitelist", result["whitelist"], has_item(self.echo_acc1))
        check_that("contract blacklist", result["blacklist"], has_item(self.echo_acc0))
        lcc.set_step("Remove accounts from whitelist and blacklist and check that accounts were removed")
        contract_whitelist_operation = self.echo_ops.get_contract_whitelist_operation(
            echo=self.echo,
            sender=self.echo_acc0,
            contract=contract_id,
            remove_from_whitelist=[self.echo_acc1],
            remove_from_blacklist=[self.echo_acc0]
        )
        collected_contract_whitelist = self.collect_operations(
            contract_whitelist_operation, self.__database_api_identifier
        )
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_contract_whitelist)
        response_id = self.send_request(
            self.get_request("get_contract_pool_whitelist", [contract_id]), self.__database_api_identifier
        )
        result = self.get_response(response_id)["result"]
        check_that("contract whitelist", result["whitelist"], equal_to([]))
        check_that("contract blacklist", result["blacklist"], equal_to([]))

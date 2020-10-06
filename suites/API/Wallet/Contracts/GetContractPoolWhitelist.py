# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_contract_pool_whitelist'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_contracts", "wallet_get_contract_pool_whitelist")
@lcc.suite("Check work of method 'get_contract_pool_whitelist'", rank=1)
class GetContractPoolWhitelist(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc5 = None
        self.echo_acc6 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")
        self.valid_contract_id = None

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
        self.echo_acc5 = self.get_account_id(
            self.accounts[5], self.__database_api_identifier, self.__registration_api_identifier
        )
        self.echo_acc6 = self.get_account_id(
            self.accounts[6], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info(
            "Echo accounts are: #1='{}', #2='{}', #3='{}'".format(self.echo_acc0, self.echo_acc5, self.echo_acc6)
        )
        self.valid_contract_id = self.utils.get_contract_id(
            self, self.echo_acc0, self.contract, self.__database_api_identifier
        )

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_contract_pool_whitelist'")
    def method_main_check(self):
        full_whitelist = []
        lcc.set_step("Add fee pool to perform two calls contract 'greet' method")
        operation_method = self.echo_ops.get_contract_call_operation(
            echo=self.echo, registrar=self.echo_acc0, bytecode=self.greet, callee=self.valid_contract_id
        )
        needed_fee = self.get_required_fee(operation_method, self.__database_api_identifier)["amount"]
        start_fee_pool_balance = needed_fee * 2
        self.utils.perform_contract_fund_pool_operation(
            self, self.echo_acc0, self.valid_contract_id, start_fee_pool_balance, self.__database_api_identifier
        )
        lcc.log_info("'{}' assets added successfully".format(start_fee_pool_balance))

        lcc.set_step("Add two accounts to whitelist")
        whitelist = [self.echo_acc5, self.echo_acc6]
        for account in whitelist:
            full_whitelist.append(account)
            full_whitelist = sorted(full_whitelist, key=self.get_value_for_sorting_func)
        self.utils.perform_contract_whitelist_operation(
            self, self.echo_acc0, self.valid_contract_id, self.__database_api_identifier, add_to_whitelist=whitelist
        )
        lcc.log_info("'{}' accounts added to '{}' contract whitelist".format(full_whitelist, self.valid_contract_id))

        lcc.set_step("Сheck get_contract_pool_whitelist method")
        response = self.send_wallet_request("get_contract_pool_whitelist", [self.valid_contract_id], log_response=False)['result']
        check_that("contract whitelist account", response['whitelist'], equal_to(whitelist))

# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_contract_pool_balance'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_contracts", "wallet_get_contract_pool_balance")
@lcc.suite("Check work of method 'get_contract_pool_balance'", rank=1)
class GetContractPoolBalance(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
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
        lcc.log_info("Echo account are: '{}'".format(self.echo_acc0))
        self.valid_contract_id = self.utils.get_contract_id(
            self, self.echo_acc0, self.contract, self.__database_api_identifier
        )

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_contract_pool_balance'")
    def method_main_check(self, get_random_integer_up_to_hundred):
        start_fee_pool_balance = get_random_integer_up_to_hundred
        lcc.set_step("Сheck get_contract_pool_balance method")
        response = self.send_wallet_request(
            "get_contract_pool_balance", [self.valid_contract_id], log_response=False
        )['result']
        check_that("pool amount", response['amount'], equal_to(0))
        check_that("pool asset_id", response['asset_id'], equal_to(self.echo_asset))
        lcc.set_step("Add fee pool to contract")
        self.utils.perform_contract_fund_pool_operation(
            self, self.echo_acc0, self.valid_contract_id, start_fee_pool_balance, self.__database_api_identifier
        )
        lcc.log_info(
            "Added '{}' assets value to '{}' contract fee pool successfully".format(
                start_fee_pool_balance, self.valid_contract_id
            )
        )
        lcc.set_step("Сheck that contract pool balance updated")
        response = self.send_wallet_request(
            "get_contract_pool_balance", [self.valid_contract_id], log_response=False
        )['result']
        check_that("pool amount", response['amount'], equal_to(start_fee_pool_balance))
        check_that("pool asset_id", response['asset_id'], equal_to(self.echo_asset))

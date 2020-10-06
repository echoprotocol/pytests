# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import WALLET_PASSWORD, INIT4_PK

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'contract_fund_fee_pool'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_contracts", "wallet_contract_fund_fee_pool")
@lcc.suite("Check work of method 'contract_fund_fee_pool'", rank=1)
class ContractFundFeePool(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")
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
        self.init4 = self.get_account_id(
            'init4', self.__database_api_identifier, self.__registration_api_identifier
        )
        self.valid_contract_id = self.utils.get_contract_id(
            self, self.init4, self.contract, self.__database_api_identifier, signer=INIT4_PK
        )
        lcc.log_info("Echo account are: '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_contract_fund_fee_pool'")
    def method_main_check(self, get_random_integer_up_to_hundred):
        fee_pool_balance = get_random_integer_up_to_hundred

        lcc.set_step("Unlock wallet to register account")
        response = self.send_wallet_request("is_new", [], log_response=False)
        if response['result']:
            self.send_wallet_request("set_password", [WALLET_PASSWORD], log_response=False)
        response = self.send_wallet_request("is_locked", [], log_response=False)
        if response['result']:
            self.send_wallet_request("unlock", [WALLET_PASSWORD], log_response=False)
        lcc.log_info("Wallet unlocked")
        lcc.set_step("Import key")
        self.send_wallet_request("import_key", ['init4', INIT4_PK], log_response=False)
        lcc.log_info("Key imported")

        lcc.set_step("Сheck contract_fund_fee_pool method")
        result = self.send_wallet_request("contract_fund_fee_pool", [self.init4, self.valid_contract_id, fee_pool_balance, True], log_response=False)['result']
        check_that('amount', result['operations'][0][1]["value"]["amount"], equal_to(fee_pool_balance))

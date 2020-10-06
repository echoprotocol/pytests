# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT4_PK

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'whitelist_contract_pool'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_contracts", "wallet_whitelist_contract_pool")
@lcc.suite("Check work of method 'whitelist_contract_pool'", rank=1)
class WhitelistContractPool(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.init4 = None
        self.echo_acc6 = None
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
        self.echo_acc6 = self.get_account_id(
            self.accounts[6], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo accounts are: #1 = '{}', #2 = '{}', #3 = '{}'".format(self.echo_acc0, self.init4, self.echo_acc6))
        self.valid_contract_id = self.utils.get_contract_id(
            self, self.init4, self.contract, self.__database_api_identifier, signer=INIT4_PK
        )

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_whitelist_contract_pool'")
    def method_main_check(self):
        self.unlock_wallet()
        lcc.set_step("Import key")
        self.send_wallet_request("import_key", ['init4', INIT4_PK], log_response=False)
        lcc.log_info("Key imported")

        lcc.set_step("Сheck whitelist_contract_pool method")
        response = self.send_wallet_request("whitelist_contract_pool", [self.init4, self.valid_contract_id, [self.echo_acc6], [], [], [], True], log_response=False)['result']
        check_that('contract', response['operations'][0][1]['contract'], equal_to(self.valid_contract_id))
        check_that('add_to_whitelist', response['operations'][0][1]['add_to_whitelist'], equal_to([self.echo_acc6]))
        check_that('remove_from_whitelist', response['operations'][0][1]['remove_from_whitelist'], equal_to([]))
        check_that('add_to_blacklist', response['operations'][0][1]['add_to_blacklist'], equal_to([]))
        check_that('remove_from_whitelist', response['operations'][0][1]['remove_from_whitelist'], equal_to([]))

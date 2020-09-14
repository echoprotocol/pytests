# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from project import WALLET_PASSWORD, INIT4_PK

SUITE = {
    "description": "Method 'dump_private_keys'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_keys", "wallet_dump_private_keys")
@lcc.suite("Check work of method 'dump_private_keys'", rank=1)
class DumpPrivateKeys(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_dump_private_keys'")
    def method_main_check(self, get_random_valid_account_name, get_random_eth_address):
        new_account = get_random_valid_account_name
        evm_address = get_random_eth_address

        lcc.set_step("Unlock wallet to register account")
        response = self.send_wallet_request("is_new", [], log_response=False)
        if response['result']:
            self.send_wallet_request("set_password", [WALLET_PASSWORD], log_response=False)
        response = self.send_wallet_request("is_locked", [], log_response=False)
        if response['result']:
            self.send_wallet_request("unlock", [WALLET_PASSWORD], log_response=False)
        lcc.log_info("Wallet unlocked")

        lcc.set_step("Add init4 to 'dump_private_keys'")
        response = self.send_wallet_request("dump_private_keys", [], log_response=False)
        if not any(INIT4_PK in sublist for sublist in response['result']):
            self.send_wallet_request('import_key', ['init4', INIT4_PK], log_response=False)
        lcc.log_info("Init4 added to 'dump_private_keys'")
        lcc.set_step("Add a new account that is not in dump_private_keys")
        lcc.log_info("Get suggested brain key")
        suggest_brain_key = self.send_wallet_request("suggest_brain_key", [], log_response=False)['result']
        lcc.log_info("Check that this key not in wallet")
        wallet_contain_status = any(suggest_brain_key['active_pub_key'] in sublist for sublist in response['result'])
        check_that("wallet contain key status", wallet_contain_status, equal_to(False))
        lcc.set_step("Register new account")
        response = self.send_wallet_request(
            "register_account",
            [
                new_account,
                suggest_brain_key['active_pub_key'],
                suggest_brain_key['active_pub_key'],
                "init4",
                evm_address,
                True
            ],
            log_response=True)
        lcc.log_info("New account created")
        self.produce_block(self.__database_api_identifier)
        lcc.set_step("Import new account key to wallet")
        self.send_wallet_request('import_key', [new_account, suggest_brain_key['active_priv_key']], log_response=False)
        lcc.log_info("Check that new account added to dump_private_keys")
        response = self.send_wallet_request("dump_private_keys", [], log_response=False)
        wallet_contain_status = any(suggest_brain_key['active_pub_key'] in sublist for sublist in response['result'])
        check_that("wallet contain key status", wallet_contain_status, equal_to(True))

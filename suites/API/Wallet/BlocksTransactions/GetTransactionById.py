# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, equal_to

SUITE = {
    "description": "Method 'get_transaction_by_id'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_blocks_transactions", "wallet_get_transaction_by_id")
@lcc.suite("Check work of method 'get_transaction_by_id'", rank=1)
class GetTransactionById(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.init4 = None

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

        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)
        lcc.log_info("Echo account are: #1='{}'".format(self.init4))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_transaction_by_id'")
    def method_main_check(self, get_random_valid_account_name, get_random_eth_address):
        new_account = get_random_valid_account_name
        evm_address = get_random_eth_address
        public_key = self.store_new_account(new_account)

        self.unlock_wallet()
        self.import_key('init4')

        lcc.set_step("Create a transaction to generate account address")
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)

        register_account = self.send_wallet_request(
            "register_account", [new_account, public_key, public_key, self.init4, evm_address, True],
            log_response=False
        )
        signed_transaction = register_account['result'][0]
        tx_id = register_account['result'][1]
        transaction = self.send_wallet_request("get_transaction_by_id", [tx_id], log_response=False)['result']
        check_that_in(
            transaction,
            "ref_block_num",
            equal_to(signed_transaction['ref_block_num']),
            "ref_block_prefix",
            equal_to(signed_transaction['ref_block_prefix']),
            "expiration",
            equal_to(signed_transaction['expiration']),
            "operations",
            equal_to(signed_transaction['operations']),
            "signatures",
            equal_to(signed_transaction['signatures']),
            quiet=True
        )

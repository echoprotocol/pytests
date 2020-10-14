# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, not_equal_to, require_that

SUITE = {
    "description": "Method 'create_committee_member'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_committee_member", "wallet_create_committee_member")
@lcc.suite("Check work of method 'create_committee_member'", rank=1)
class CreateCommitteeMember(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

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

        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        lcc.log_info("Echo account are: #1='{}'".format(self.init5))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_create_committee_member'")
    def method_main_check(self, get_random_eth_address, get_random_btc_public_key):
        eth_address = get_random_eth_address
        btc_public_key = get_random_btc_public_key

        self.unlock_wallet()
        self.import_key('init5')

        lcc.set_step("Check method create_committee_member")
        lcc.log_info("Make sure that {} account is not yet a committee member")
        response_id = self.send_request(
            self.get_request("get_committee_member_by_account", [self.init5]), self.__database_api_identifier
        )
        committee_member = self.get_response(response_id)["result"]
        require_that("commitee member object", committee_member, equal_to(None))

        lcc.log_info('Create committee member')
        self.send_wallet_request(
            "create_committee_member", [self.init5, "", 1000, eth_address, btc_public_key, True], log_response=True
        )
        self.produce_block(self.__database_api_identifier)
        lcc.set_step("Check that new committee created")
        response_id = self.send_request(
            self.get_request("get_committee_member_by_account", [self.init5]), self.__database_api_identifier
        )
        committee_member = self.get_response(response_id)["result"]
        check_that("new commitee member", committee_member, not_equal_to(None))

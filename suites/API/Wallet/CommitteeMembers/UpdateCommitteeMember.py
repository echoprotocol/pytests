# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT5_PK

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, not_equal_to

SUITE = {
    "description": "Method 'update_committee_member'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_committee_member", "wallet_update_committee_member")
@lcc.suite("Check work of method 'update_committee_member'", rank=1)
class UpdateCommitteeMember(WalletBaseTest, BaseTest):

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.depends_on("API.Wallet.CommitteeMembers.CreateCommitteeMember.CreateCommitteeMember.method_main_check")
    @lcc.test("Simple work of method 'wallet_update_committee_member'")
    def method_main_check(self, get_random_eth_address, get_random_btc_public_key):
        self.unlock_wallet()

        lcc.set_step("Import key")
        self.send_wallet_request("import_key", ['init5', INIT5_PK], log_response=False)
        lcc.log_info("Key imported")

        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)

        eth_address = get_random_eth_address
        btc_public_key = get_random_btc_public_key
        lcc.set_step("Check method update_committee_member")

        response_id = self.send_request(
            self.get_request("get_committee_member_by_account", [self.init5]), self.__database_api_identifier
        )
        committee_member_before_update = self.get_response(response_id)["result"]

        self.send_wallet_request(
            "update_committee_member", [self.init5, '', eth_address, btc_public_key, True], log_response=False
        )
        self.produce_block(self.__database_api_identifier)

        response_id = self.send_request(
            self.get_request("get_committee_member_by_account", [self.init5]), self.__database_api_identifier
        )
        committee_member_after_update = self.get_response(response_id)["result"]

        check_that("new commitee member", committee_member_before_update, not_equal_to(committee_member_after_update))

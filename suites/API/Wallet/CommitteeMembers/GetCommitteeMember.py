# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_committee_member'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_committee_member", "wallet_get_committee_member")
@lcc.suite("Check work of method 'get_committee_member'", rank=1)
class GetCommitteeMember(WalletBaseTest, BaseTest):

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
    @lcc.test("Simple work of method 'wallet_get_committee_member'")
    def method_main_check(self):
        lcc.set_step("Check get_committee_member method")
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        committee_member = self.send_wallet_request("get_committee_member", ['init5'], log_response=True)['result']
        check_that('committee member account id', self.init5, equal_to(committee_member['committee_member_account']))

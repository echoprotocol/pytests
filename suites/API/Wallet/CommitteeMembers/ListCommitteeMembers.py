# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_list, is_str

SUITE = {
    "description": "Method 'list_committee_members'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_committee_member", "wallet_list_committee_members")
@lcc.suite("Check work of method 'list_committee_members'", rank=1)
class ListCommitteeMembers(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_list_committee_members'")
    def method_main_check(self, get_random_eth_address, get_random_btc_public_key):
        committee_members = self.send_wallet_request("list_committee_members", ['', 10], log_response=False)['result']
        check_that("list_committee_members", committee_members, is_list(), quiet=True)
        check_that('committee_member', committee_members[0][0], is_str(), quiet=True)
        if self.type_validator.is_committee_member_id(committee_members[0][1]):
            lcc.log_info("Correct format of committe member id")
        else:
            lcc.log_error("Wrong format of committee member id")

# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_str, is_true, require_that

SUITE = {
    "description": "Method 'get_git_revision'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_get_git_revision")
@lcc.suite("Check work of method 'get_git_revision'", rank=1)
class GetGitRevision(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_git_revision'")
    def method_main_check(self):
        lcc.set_step('Check get_git_revision method')
        result = self.send_wallet_request("get_git_revision", [], log_response=False)['result']
        if not self.type_validator.is_hex(result["ECHO_GIT_REVISION_SHA"]):
            lcc.log_error("Wrong format of 'ECHO_GIT_REVISION_SHA', got: {}".format(result["ECHO_GIT_REVISION_SHA"]))
        else:
            lcc.log_info("'ECHO_GIT_REVISION_SHA' has correct format: hex")

        for index, unix_timestamp_part in enumerate(result['ECHO_GIT_REVISION_UNIX_TIMESTAMP'].split(" ")):
            if index:
                check = is_str
                part = unix_timestamp_part
                name = 'ECHO_GIT_REVISION_UNIX_TIMESTAMP part'
            else:
                check = is_true
                part = unix_timestamp_part.isdigit()
                name = 'ECHO_GIT_REVISION_UNIX_TIMESTAMP is digit string'
            require_that(name, part, check())
        require_that('result', result["ECHO_GIT_REVISION_DESCRIPTION"], is_str())

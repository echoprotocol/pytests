# -*- coding: utf-8 -*-
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, has_entry, is_not_none, require_that

SUITE = {
    "description": "Method 'help'"
}


@lcc.prop("main", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "wallet_api", "wallet_info_help", "wallet_help")
@lcc.suite("Check work of method 'help'", rank=1)
class Help(WalletBaseTest):

    def __init__(self):
        super().__init__()

    @lcc.test("Simple work of method 'help'")
    def method_main_check(self):
        lcc.set_step("Call method 'help'")
        response = self.send_wallet_request("help")
        response_with_parameter = self.send_wallet_request("help", ["transfer"])
        require_that("'result'", response_with_parameter["result"], is_not_none(), quiet=True)
        require_that("'result'", response["result"], is_not_none(), quiet=True)


@lcc.prop("negative", "type")
@lcc.tags("api", "wallet_api", "wallet_info_help", "wallet_help")
@lcc.suite("Negative testing of method 'help'", rank=3)
class NegativeTesting(WalletBaseTest):

    @lcc.prop("type", "method")
    @lcc.test("Call method with params of all types")
    @lcc.depends_on("API.Wallet.InfoHelp.Help.Help.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            if i == 4:
                continue
            response = self.send_wallet_request("help", random_values[i], negative=True)
            check_that(
                "'get_account_count' return error message with '{}' params".format(random_type_names[i]),
                response,
                has_entry("error"),
                quiet=True
            )

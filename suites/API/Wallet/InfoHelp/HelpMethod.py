# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from lemoncheesecake.matching import require_that, has_entry, is_not_none, check_that

from common.wallet_base_test import WalletBaseTest

SUITE = {
    "description": "Method 'help_method'"
}


@lcc.prop("main", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "wallet_api", "wallet_help_method")
@lcc.suite("Check work of method 'help_method'", rank=1)
class HelpMethod(WalletBaseTest):

    def __init__(self):
        super().__init__()

    # todo: bug ECHO-2217
    @lcc.disabled()
    @lcc.test("Simple work of method 'help_method'")
    def method_main_check(self):
        lcc.set_step("Call method 'help_method'")
        response = self.send_wallet_request("help_method", "get_object", log_response=True)
        require_that("'result'", response["result"], is_not_none(), quiet=True)


@lcc.prop("negative", "type")
@lcc.tags("api", "wallet_api", "wallet_help_method")
@lcc.suite("Negative testing of method 'help_method'", rank=3)
class NegativeTesting(WalletBaseTest):

    @lcc.prop("type", "method")
    @lcc.test("Call method with params of all types")
    # todo: bug ECHO-2217
    # @lcc.depends_on("API.Wallet.InfoHelp.HelpMethod.HelpMethod.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            if i == 4:
                continue
            response = self.send_wallet_request("help_method", random_values[i], negative=True)
            check_that(
                "'get_account_count' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True
            )

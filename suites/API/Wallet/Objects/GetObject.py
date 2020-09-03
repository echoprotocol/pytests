# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from lemoncheesecake.matching import require_that, has_entry, is_not_none, check_that
from common.wallet_base_test import WalletBaseTest

SUITE = {
    "description": "Method 'get_object'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "wallet_api", "wallet_get_object")
@lcc.suite("Check work of method 'get_object'", rank=1)
class GetObject(WalletBaseTest):

    def __init__(self):
        super().__init__()

    @lcc.test("Simple work of method 'get_object'")
    def method_main_check(self):
        lcc.set_step("Call method 'get_object'")
        response = self.send_wallet_request("get_object", ["1.2.10"])
        require_that("'result'", response, is_not_none(), quiet=True)

        lcc.set_step("Checking account result")
        account_info = response["result"][0]
        self.object_validator.validate_account_object(self, account_info)


@lcc.prop("negative", "type")
@lcc.tags("api", "wallet_api", "wallet_get_object")
@lcc.suite("Negative testing of method 'get_object'", rank=3)
class NegativeTesting(WalletBaseTest):

    @lcc.prop("type", "method")
    @lcc.test("Call method with params of all types")
    @lcc.depends_on("API.Wallet.Objects.GetObject.GetObject.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            if i == 4:
                continue
            response = self.send_wallet_request("get_object", random_values[i], negative=True)
            check_that(
                "'get_account_count' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True
            )

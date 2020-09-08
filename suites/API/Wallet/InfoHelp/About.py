# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from lemoncheesecake.matching import require_that, has_entry, is_not_none, check_that, has_length, equal_to

from common.wallet_base_test import WalletBaseTest

SUITE = {
    "description": "Method 'about'"
}


@lcc.prop("main", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "wallet_api", "wallet_about")
@lcc.suite("Check work of method 'about'", rank=1)
class About(WalletBaseTest):

    def __init__(self):
        super().__init__()

    @lcc.test("Simple work of method 'about'")
    def method_main_check(self):
        lcc.set_step("Call method 'about'")
        response = self.send_wallet_request("about")
        require_that("'result'", response["result"], is_not_none(), quiet=True)

        lcc.set_step("Check result")
        result = response["result"]
        if require_that("result", result, has_length(10)):
            check_that("blockchain_name", result["blockchain_name"], equal_to("ECHO"))
            check_that("client_version", result["client_version"], equal_to("0.22-rc.1"))
            if not self.type_validator.is_hex(result["echo_revision"]):
                lcc.log_error("Wrong format of 'echo_revision', got: {}".format(result["echo_revision"]))
            else:
                lcc.log_info("'echo_revision' has correct format: hex")
            if not self.type_validator.check_age(result["echo_revision_age"]):
                lcc.log_error("Wrong format of 'echo_revision_age', got: {}".format(result["echo_revision_age"]))
            else:
                lcc.log_info("'echo_revision_age' has correct format: age time")
            if not self.type_validator.is_hex(result["fc_revision"]):
                lcc.log_error("Wrong format of 'fc_revision', got: {}".format(result["fc_revision"]))
            else:
                lcc.log_info("'fc_revision' has correct format: hex")
            if not self.type_validator.check_age(result["fc_revision_age"]):
                lcc.log_error("Wrong format of 'fc_revision_age', got: {}".format(result["fc_revision_age"]))
            else:
                lcc.log_info("'fc_revision_age' has correct format: age time")
            check_that("compile_date", result["compile_date"], equal_to("compiled on Sep  4 2020 at 13:59:47"))
            check_that("boost_version", result["boost_version"], equal_to("1.70"))
            check_that("openssl_version", result["openssl_version"], equal_to("OpenSSL 1.0.2g  1 Mar 2016"))
            check_that("build", result["build"], equal_to("linux 64-bit"))


@lcc.prop("negative", "type")
@lcc.tags("api", "wallet_api", "wallet_about")
@lcc.suite("Negative testing of method 'about'", rank=3)
class NegativeTesting(WalletBaseTest):

    @lcc.prop("type", "method")
    @lcc.test("Call method with params of all types")
    @lcc.depends_on("API.Wallet.InfoHelp.About.About.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            if i == 4:
                continue
            response = self.send_wallet_request("about", random_values[i], negative=True)
            check_that(
                "'get_account_count' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True
            )

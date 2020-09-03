# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from lemoncheesecake.matching import require_that, has_entry, is_not_none, check_that, has_length, is_integer, \
    is_list, equal_to

from common.wallet_base_test import WalletBaseTest
from echopy import Echo

from project import BASE_URL

SUITE = {
    "description": "Method 'info'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "wallet_api", "wallet_info")
@lcc.suite("Check work of method 'info'", rank=1)
class Info(WalletBaseTest):

    def __init__(self):
        super().__init__()

    @lcc.test("Simple work of method 'info'")
    def method_main_check(self):
        lcc.set_step("Call method 'info'")
        response = self.send_wallet_request("info", [])
        require_that("'result'", response["result"], is_not_none(), quiet=True)

        lcc.set_step("Check method 'info' result")
        result = response["result"]
        if check_that("result", result, has_length(6)):
            require_that("head_block_num", result["head_block_num"], is_integer(), quiet=True)
            if not self.type_validator.is_hex(result["head_block_id"]):
                lcc.log_error("Wrong format of 'log_value', got: {}".format(result["head_block_id"]))
            else:
                lcc.log_info("'head_block_id' has correct format: hex")
            if not self.type_validator.check_age(result["head_block_age"]):
                lcc.log_error("Wrong format of 'head_block_age', got: {}".format(result["head_block_age"]))
            else:
                lcc.log_info("'head_block_age' has correct format: age time")
            if not self.type_validator.is_hex(result["chain_id"]):
                lcc.log_error("Wrong format of 'chain_id', got: {}".format(response["result"]))
            else:
                lcc.log_info("'chain_id' has correct format: hex")
            if require_that("active_committee_members", result["active_committee_members"], is_list()):
                for active_committee_member in result["active_committee_members"]:
                    if require_that("active_committee_member", active_committee_member, is_list()):
                        if not self.type_validator.is_account_id(active_committee_member[1]):
                            lcc.log_error(
                                "Wrong format of 'active_committee_member', got: {}".format(active_committee_member[1]))
                        else:
                            lcc.log_info("'active_committee_member' has correct format: account_id")
                        if not self.type_validator.is_committee_member_id(active_committee_member[0]):
                            lcc.log_error(
                                "Wrong format of 'active_committee_member', got: {}".format(active_committee_member[0]))
                        else:
                            lcc.log_info("'active_committee_member' has correct format: committee_member_id")


@lcc.prop("positive", "type")
@lcc.tags("api", "wallet_api", "wallet_info")
@lcc.suite("Positive testing of method 'info'", rank=2)
class PositiveTesting(WalletBaseTest):

    def __init__(self):
        super().__init__()
        self.echopy = Echo()

    def setup_suite(self):
        self.echopy.connect(BASE_URL)

    def teardown_suite(self):
        self.echopy.disconnect()

    @lcc.depends_on("API.Wallet.InfoHelp.Info.Info.method_main_check")
    @lcc.test("Compare result of method 'info' with DatabaseAPI")
    def compare_result_with_database_api(self):
        lcc.set_step("Get result of method 'info'")
        result = self.send_wallet_request("info", [])["result"]
        lcc.log_info("Successful")

        lcc.set_step("Compare 'chain_id'")
        database_chain_id = self.echopy.api.database.get_chain_id()
        check_that("chain_id", database_chain_id, equal_to(result["chain_id"]))

        lcc.set_step("Compare 'active_committee_members'")
        database_active_committee_members = self.echopy.api.database.get_global_properties()["active_committee_members"]
        check_that("active_committee_members", database_active_committee_members,
                   equal_to(result["active_committee_members"]))


@lcc.prop("negative", "type")
@lcc.tags("api", "wallet_api", "wallet_info")
@lcc.suite("Negative testing of method 'info'", rank=3)
class NegativeTesting(WalletBaseTest):

    @lcc.prop("type", "method")
    @lcc.test("Call method with params of all types")
    @lcc.depends_on("API.Wallet.InfoHelp.Info.Info.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            if i == 4:
                continue
            response = self.send_wallet_request("info", random_values[i], negative=True)
            check_that(
                "'get_account_count' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True
            )

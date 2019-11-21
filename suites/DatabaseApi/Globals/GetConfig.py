# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, check_that, has_length, has_entry, is_str

from common.base_test import BaseTest
from project import BASE_ASSET_SYMBOL

SUITE = {
    "description": "Method 'get_config'"
}


@lcc.prop("main", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_globals", "get_config")
@lcc.suite("Check work of method 'get_config'", rank=1)
class GetConfig(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.test("Simple work of method 'get_config'")
    def method_main_check(self):
        lcc.set_step("Get config")
        response_id = self.send_request(self.get_request("get_config"), self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_config'")

        lcc.set_step("Check main fields")
        echo_config_symbols = ["ECHO_SYMBOL", "ECHO_ADDRESS_PREFIX", "ECHO_ED_PREFIX"]
        echo_configs = ["ECHO_MIN_ACCOUNT_NAME_LENGTH", "ECHO_MAX_ACCOUNT_NAME_LENGTH", "ECHO_MIN_ASSET_SYMBOL_LENGTH",
                        "ECHO_MAX_ASSET_SYMBOL_LENGTH", "ECHO_MAX_SHARE_SUPPLY", "ECHO_MAX_PAY_RATE",
                        "ECHO_MAX_SIG_CHECK_DEPTH", "ECHO_MIN_TRANSACTION_SIZE_LIMIT",
                        "ECHO_DEFAULT_MAX_TRANSACTION_SIZE", "ECHO_MIN_TRANSACTION_EXPIRATION_LIMIT",
                        "ECHO_DEFAULT_MAX_BLOCK_SIZE", "ECHO_DEFAULT_MAX_TIME_UNTIL_EXPIRATION",
                        "ECHO_DEFAULT_MAINTENANCE_INTERVAL", "ECHO_DEFAULT_MAINTENANCE_DURATION_SECONDS",
                        "ECHO_MIN_UNDO_HISTORY", "ECHO_MAX_UNDO_HISTORY", "ECHO_MIN_BLOCK_SIZE_LIMIT",
                        "ECHO_BLOCKCHAIN_PRECISION", "ECHO_BLOCKCHAIN_PRECISION_DIGITS", "ECHO_DEFAULT_TRANSFER_FEE",
                        "ECHO_MAX_INSTANCE_ID", "ECHO_100_PERCENT", "ECHO_1_PERCENT",
                        "ECHO_DEFAULT_PRICE_FEED_LIFETIME", "ECHO_DEFAULT_MAX_AUTHORITY_MEMBERSHIP",
                        "ECHO_DEFAULT_MAX_ASSET_WHITELIST_AUTHORITIES", "ECHO_DEFAULT_MAX_ASSET_FEED_PUBLISHERS",
                        "ECHO_COLLATERAL_RATIO_DENOM", "ECHO_MIN_COLLATERAL_RATIO", "ECHO_MAX_COLLATERAL_RATIO",
                        "ECHO_DEFAULT_MAINTENANCE_COLLATERAL_RATIO", "ECHO_DEFAULT_MAX_SHORT_SQUEEZE_RATIO",
                        "ECHO_DEFAULT_MAX_PROPOSAL_LIFETIME_SEC",
                        "ECHO_DEFAULT_COMMITTEE_PROPOSAL_REVIEW_PERIOD_SEC", "ECHO_MAX_URL_LENGTH",
                        "ECHO_DEFAULT_MIN_COMMITTEE_MEMBER_COUNT", "ECHO_DEFAULT_MINIMUM_FEEDS",
                        "ECHO_REVERSIBLE_BLOCKS_COUNT", "ECHO_DEFAULT_COMMITTEE_FREEZE_DURATION_SECONDS"]
        echo_config_accounts = ["ECHO_COMMITTEE_ACCOUNT", "ECHO_RELAXED_COMMITTEE_ACCOUNT", "ECHO_NULL_ACCOUNT",
                                "ECHO_TEMP_ACCOUNT", "ECHO_NULL_AUTHORITY_ACCOUNT", "ECHO_PROXY_TO_SELF_ACCOUNT"]
        if check_that("config", response["result"], has_length(49)):
            for echo_config_symbol in echo_config_symbols:
                check_that_in(
                    response["result"],
                    echo_config_symbol, is_str(BASE_ASSET_SYMBOL),
                    quiet=True
                )
            for echo_config in echo_configs:
                self.check_uint64_numbers(response["result"], echo_config, quiet=True)
            for echo_config_account in echo_config_accounts:
                if not self.type_validator.is_account_id(response["result"][echo_config_account]):
                    lcc.log_error("Wrong format of '{}', got: {}".format(echo_config_account, response["result"][
                        echo_config_account]))
                else:
                    lcc.log_info("'{}' has correct format: account_id".format(echo_config_account))


@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_globals", "get_config")
@lcc.suite("Negative testing of method 'get_config'", rank=2)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__api_identifier))

    @lcc.test("Call method with params of all types")
    @lcc.tags("Bug: 'ECHO-680'")
    @lcc.depends_on("DatabaseApi.Globals.GetConfig.GetConfig.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            # todo: remove if. Bug: "ECHO-680"
            if i == 4:
                continue
            response_id = self.send_request(self.get_request("get_config", random_values[i]),
                                            self.__api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_config' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True
            )

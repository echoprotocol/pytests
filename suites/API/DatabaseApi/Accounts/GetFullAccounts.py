# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import (
    check_that, check_that_in, equal_to, has_length, is_dict, is_list, is_str, require_that
)

SUITE = {
    "description": "Methods: 'get_full_accounts', 'get_objects' (account balance & account statistics objects)"
}


@lcc.prop("main", "type")
@lcc.tags("api", "database_api", "database_api_accounts", "get_full_accounts", "database_api_objects", "get_objects")
@lcc.suite(
    "Check work of methods: 'get_full_accounts', 'get_objects' (account balance & account statistics objects)", rank=1
)
class GetFullAccounts(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def check_fields_account_ids_format(self, response, field):
        if not self.type_validator.is_account_id(response[field]):
            lcc.log_error("Wrong format of '{}', got: {}".format(field, response[field]))
        else:
            lcc.log_info("'{}' has correct format: account_object_type".format(field))

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.test(
        "Simple work of methods: 'get_full_accounts', 'get_objects' (account balance & account statistics objects)"
    )
    def method_main_check(self):
        lcc.set_step("Get full info about default accounts")
        params = ["1.2.0", "1.2.1"]
        response_id = self.send_request(
            self.get_request("get_full_accounts", [params, False]), self.__database_api_identifier
        )
        results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_full_accounts' with params: {}".format(params))

        lcc.set_step("Check length of received accounts")
        require_that("'list of received accounts'", results, has_length(len(params)), quiet=True)

        for i, result in enumerate(results):
            lcc.set_step("Checking account #{} - '{}'".format(i, params[i]))
            check_that("account_id", result[0], equal_to(params[i]), quiet=True)
            full_account_info = result[1]
            if check_that("full_account_info", full_account_info, has_length(7), quiet=True):
                account_info = full_account_info.get("account")
                self.object_validator.validate_account_object(self, account_info)

                lcc.set_step("Check 'statistics' field")
                check_that_in(full_account_info, "statistics", is_dict(), quiet=True)
                account_statistics = full_account_info.get("statistics")
                self.object_validator.validate_account_statistics_object(self, account_statistics)
                check_that_in(account_statistics, "owner", is_str(params[i]), quiet=True)
                lcc.set_step("Check 'registrar_name' field")
                if not self.type_validator.is_account_name(full_account_info["registrar_name"]):
                    lcc.log_error(
                        "Wrong format of 'registrar_name', got: {}".format(full_account_info["registrar_name"])
                    )
                else:
                    lcc.log_info("'registrar_name' has correct format: account_name")
                lcc.set_step("Check 'balances' field")
                check_that_in(full_account_info, "balances", is_list(), quiet=True)
                balances = full_account_info["balances"]
                if balances:
                    for j, balance in enumerate(balances):
                        lcc.set_step("Check 'balance #{}' field".format(j))
                        self.object_validator.validate_account_balance_object(self, balance)
                        check_that_in(balance, "owner", is_str(params[i]), quiet=True)
                lcc.set_step("Check 'vesting_balances' field")
                check_that_in(full_account_info, "vesting_balances", is_list(), quiet=True)
                lcc.set_step("Check 'proposals' field")
                check_that_in(full_account_info, "proposals", is_list(), quiet=True)
                lcc.set_step("Check 'assets' field")
                if check_that_in(full_account_info, "assets", is_list(), quiet=True):
                    for asset in full_account_info["assets"]:
                        if not self.type_validator.is_asset_id(asset):
                            lcc.log_error("Wrong format of 'asset', got: {}".format(asset))
                        else:
                            lcc.log_info("'asset' has correct format: asset_id")

        lcc.set_step("Get account balance object by id")
        account_balance_id = balance["id"]
        params = [account_balance_id]
        response_id = self.send_request(self.get_request("get_objects", [params]), self.__database_api_identifier)
        get_objects_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with param: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that("'list of received objects'", get_objects_results, has_length(len(params)), quiet=True)

        lcc.set_step(
            "Check the identity of returned results of api-methods:'get_full_accounts' (balance), 'get_objects'"
        )
        require_that('results', get_objects_results[0], equal_to(balance), quiet=True)

        lcc.set_step("Get account statistics object by id")
        account_statistics_id = account_statistics["id"]
        params = [account_statistics_id]
        response_id = self.send_request(self.get_request("get_objects", [params]), self.__database_api_identifier)
        get_objects_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with param: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that("'list of received objects'", get_objects_results, has_length(len(params)), quiet=True)

        lcc.set_step(
            "Check the identity of returned results of api-methods:'get_full_accounts' (statistics), 'get_objects'"
        )
        require_that('results', get_objects_results[0], equal_to(account_statistics), quiet=True)

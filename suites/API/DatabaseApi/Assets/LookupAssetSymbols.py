# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from project import ECHO_ASSET_SYMBOL

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, check_that_in, equal_to, is_none

SUITE = {
    "description": "Method 'lookup_asset_symbols'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_assets", "lookup_asset_symbols")
@lcc.suite("Check work of method 'lookup_asset_symbols'", rank=1)
class LookupAssetSymbols(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.echo_symbol = ECHO_ASSET_SYMBOL

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.test("Simple work of method 'lookup_asset_symbols'")
    def method_main_check(self):
        lcc.set_step("Lookup default asset of the chain using it symbol")
        symbols_or_ids = [self.echo_symbol]
        response_id = self.send_request(
            self.get_request("lookup_asset_symbols", [symbols_or_ids]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call method 'lookup_asset_symbols' with symbols_or_ids='{}' parameter".format(symbols_or_ids))

        lcc.set_step("Check simple work of method 'lookup_asset_symbols'")
        asset_by_symbol = response["result"][0]
        self.object_validator.validate_asset_object(self, asset_by_symbol)

        lcc.set_step("Lookup default asset of the chain using it asset_id")
        symbols_or_ids = [self.echo_asset]
        response_id = self.send_request(
            self.get_request("lookup_asset_symbols", [symbols_or_ids]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info(
            "Call method method 'lookup_asset_symbols' with symbols_or_ids='{}' parameter".format(symbols_or_ids)
        )
        asset_by_id = response["result"][0]
        self.object_validator.validate_asset_object(self, asset_by_id)
        lcc.set_step("Compare 'lookup_asset_symbols' method calls results with different type of input params")


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_assets", "lookup_asset_symbols")
@lcc.suite("Positive testing of method 'lookup_asset_symbols'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    @staticmethod
    def proliferate_asset_names(asset_name_base, total_asset_count):
        return ['{}{}'.format(asset_name_base, 'A' * num) for num in range(total_asset_count)]

    @staticmethod
    def compare_assets(asset_info, performed_operation, asset_is_created=False):
        if performed_operation["symbol"] == asset_info["symbol"]:
            if asset_is_created:
                performed_operation["common_options"]["core_exchange_rate"]["quote"]["asset_id"] = \
                    asset_info["options"]["core_exchange_rate"]["quote"]["asset_id"]
            check_that_in(
                asset_info,
                "issuer",
                equal_to(performed_operation["issuer"]),
                "symbol",
                equal_to(performed_operation["symbol"]),
                "precision",
                equal_to(performed_operation["precision"]),
            )
            performed_options_field_name = "options"
            if asset_is_created:
                performed_options_field_name = "common_options"
            check_that_in(asset_info, "options", equal_to(performed_operation[performed_options_field_name]))

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
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Create assets using asset_create operation and lookup info about them")
    @lcc.depends_on("API.DatabaseApi.Assets.LookupAssetSymbols.LookupAssetSymbols.method_main_check")
    def lookup_info_about_created_assets(self, get_random_valid_asset_name):
        lcc.set_step("Generate assets symbols")
        asset_name_base = get_random_valid_asset_name
        total_asset_count = 2
        generated_assets = self.proliferate_asset_names(asset_name_base, total_asset_count)
        lcc.log_info('Generated asset names: {}'.format(generated_assets))

        lcc.set_step("Perform assets creation operation")
        asset_ids = []
        collected_operations = []
        for asset_symbol in generated_assets:
            asset_id, collected_operation = self.utils.get_asset_id(
                self, asset_symbol, self.__database_api_identifier, need_operation=True
            )
            asset_ids.append(asset_id)
            collected_operations.append(collected_operation)
        lcc.log_info("Assets was created, ids='{}'".format(asset_ids))

        lcc.set_step("Lookup created assets by symbols")
        response_id = self.send_request(
            self.get_request("lookup_asset_symbols", [generated_assets]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call method 'lookup_asset_symbols' with symbols_or_ids='{}' parameter".format(generated_assets))

        lcc.set_step("Check created assets")
        assets_by_symbol = response["result"]
        for collected_operation in collected_operations:
            for asset_by_symbol_info in assets_by_symbol:
                self.compare_assets(asset_by_symbol_info, collected_operation[0][1], asset_is_created=True)

        lcc.set_step("Lookup created assets by ids")
        response_id = self.send_request(
            self.get_request("lookup_asset_symbols", [asset_ids]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call method 'lookup_asset_symbols' with symbols_or_ids='{}' parameter".format(generated_assets))

        lcc.set_step("Check created assets")
        assets_by_ids = response["result"]
        for asset_by_symbol_info in assets_by_symbol:
            for asset_by_id_info in assets_by_ids:
                self.compare_assets(asset_by_id_info, asset_by_symbol_info)

        lcc.set_step("Lookup created assets by mixed input parameters (symbol and id)")
        mixed_symbols_or_ids = [asset_ids[0], generated_assets[1]]
        response_id = self.send_request(
            self.get_request("lookup_asset_symbols", [mixed_symbols_or_ids]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info(
            "Call method 'lookup_asset_symbols' with symbols_or_ids='{}' parameter".format(mixed_symbols_or_ids)
        )

        lcc.set_step("Check created assets")
        assets_by_mixed_params = response["result"]
        for asset_by_id_info in assets_by_ids:
            for asset_by_mixed_params_info in assets_by_mixed_params:
                self.compare_assets(asset_by_mixed_params_info, asset_by_id_info)

    @lcc.test("Lookup nonexistent assets")
    @lcc.depends_on("API.DatabaseApi.Assets.LookupAssetSymbols.LookupAssetSymbols.method_main_check")
    def lookup_info_about_nonexistent_assets(self):
        lcc.set_step("Generate nonexistent asset symbol")
        nonexistent_asset_symbols = [self.utils.get_nonexistent_asset_symbol(self, self.__database_api_identifier)]
        lcc.log_info("Nonexistent asset symbol: {}".format(nonexistent_asset_symbols))

        lcc.set_step("Lookup nonexistent asset by symbol")
        response_id = self.send_request(
            self.get_request("lookup_asset_symbols", [nonexistent_asset_symbols]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info(
            "Call method 'lookup_asset_symbols' with symbols_or_ids='{}' parameter".format(nonexistent_asset_symbols)
        )

        lcc.set_step("Check nonexistent asset")
        nonexistent_asset_by_symbol = response["result"]
        for nonexistent_result in nonexistent_asset_by_symbol:
            check_that("'lookup_asset_symbols result'", nonexistent_result, is_none())

        lcc.set_step("Generate nonexistent asset_id")
        nonexistent_asset_id = [self.utils.get_nonexistent_asset_id(self, self.__database_api_identifier)]
        lcc.log_info('Nonexistent asset id: {}'.format(nonexistent_asset_id))

        lcc.set_step("Lookup nonexistent asset by id")
        response_id = self.send_request(
            self.get_request("lookup_asset_symbols", [nonexistent_asset_id]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info(
            "Call method 'lookup_asset_symbols' with symbols_or_ids='{}' parameter".format(nonexistent_asset_symbols)
        )

        lcc.set_step("Check nonexistent asset")
        nonexistent_asset_by_id = response["result"]
        for nonexistent_result in nonexistent_asset_by_id:
            check_that("'get_assets result'", nonexistent_result, is_none())

    @lcc.test("Compare 'lookup_asset_symbols' result with 'get_objects' result")
    @lcc.depends_on("API.DatabaseApi.Assets.LookupAssetSymbols.LookupAssetSymbols.method_main_check")
    def compare_with_method_get_objects(self):
        lcc.set_step("Lookup ECHO asset by id")
        response_id = self.send_request(
            self.get_request("lookup_asset_symbols", [[self.echo_asset]]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call method 'lookup_asset_symbols' with symbols_or_ids='{}' parameter".format(self.echo_asset))

        asset_object_by_lookup = response["result"][0]

        lcc.set_step("Get object of ECHO asset")
        response_id = self.send_request(
            self.get_request("get_objects", [[self.echo_asset]]), self.__database_api_identifier
        )

        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_objects' with param: {}".format(self.echo_asset))
        asset_object_by_get_object = response["result"][0]

        lcc.set_step("Compare asset objects (by 'lookup_asset_symbols' and 'get_objects' methods)")
        self.compare_assets(asset_object_by_lookup, asset_object_by_get_object)

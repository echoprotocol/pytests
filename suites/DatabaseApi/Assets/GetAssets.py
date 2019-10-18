# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, equal_to, check_that, is_none

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_assets'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_assets", "get_assets")
@lcc.suite("Check work of method 'get_assets'", rank=1)
class GetAssets(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.test("Simple work of method 'get_assets'")
    def method_main_check(self):
        lcc.set_step("Get default asset of the chain")
        asset_ids = [self.echo_asset]
        response_id = self.send_request(self.get_request("get_assets", [asset_ids]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_assets' with asset_ids='{}' parameter".format(asset_ids))

        lcc.set_step("Check simple work of method 'get_assets'")
        asset = response["result"][0]

        self.object_validator.validate_asset_object(self, asset)


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_assets", "get_assets")
@lcc.suite("Positive testing of method 'get_assets'", rank=2)
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
    def check_created_asset(asset_info, performed_operation):
        if performed_operation["symbol"] == asset_info["symbol"]:
            performed_operation["common_options"]["core_exchange_rate"]["quote"]["asset_id"] = \
                asset_info["options"]["core_exchange_rate"]["quote"]["asset_id"]
            check_that_in(
                asset_info,
                "issuer", equal_to(performed_operation["issuer"]),
                "symbol", equal_to(performed_operation["symbol"]),
                "precision", equal_to(performed_operation["precision"]),
                "options", equal_to(performed_operation["common_options"])
            )

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Create assets using asset_create operation and get info about them")
    @lcc.depends_on("DatabaseApi.Assets.GetAssets.GetAssets.method_main_check")
    def get_info_about_create_assets(self, get_random_valid_asset_name):
        lcc.set_step("Generate assets symbols")
        asset_name_base = get_random_valid_asset_name
        total_asset_count = 2
        generated_assets = self.proliferate_asset_names(asset_name_base, total_asset_count)
        lcc.log_info('Generated asset names: {}'.format(generated_assets))

        lcc.set_step("Perform assets creation operation")
        asset_ids = []
        collected_operations = []
        for asset_symbol in generated_assets:
            asset_id, collected_operation = self.utils.get_asset_id(self, asset_symbol,
                                                                    self.__database_api_identifier,
                                                                    need_operation=True)
            asset_ids.append(asset_id)
            collected_operations.append(collected_operation)
        lcc.log_info("Assets was created, ids='{}'".format(asset_ids))

        lcc.set_step("Get assets")
        response_id = self.send_request(self.get_request("get_assets", [asset_ids]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_assets' with param: {}".format(asset_ids))

        lcc.set_step("Check created assets")
        assets_info = response["result"]
        for collected_operation in collected_operations:
            for asset_info in assets_info:
                self.check_created_asset(asset_info, collected_operation[0][1])

    @lcc.test("Get info about nonexistent asset id")
    @lcc.depends_on("DatabaseApi.Assets.GetAssets.GetAssets.method_main_check")
    def get_info_about_nonexistent_asset_id(self):
        lcc.set_step("Generate nonexistent asset_id")
        nonexistent_asset_id = [self.utils.get_nonexistent_asset_id(self, self.__database_api_identifier)]
        lcc.log_info('Nonexistent asset id: {}'.format(nonexistent_asset_id))

        lcc.set_step("Get assets")
        response_id = self.send_request(self.get_request("get_assets", [nonexistent_asset_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_assets' with param: {}".format(nonexistent_asset_id))

        lcc.set_step("Check nonexistent asset")
        asset_info = response["result"]
        for nonexistent_result in asset_info:
            check_that("'get_assets result'", nonexistent_result, is_none())

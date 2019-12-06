# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, equal_to, check_that, is_none, require_that, has_length

from common.base_test import BaseTest

SUITE = {
    "description": "Methods: 'get_assets', 'get_objects' (asset & dynamic asset data"
    " & bitasset data objects)"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags(
    "api", "database_api", "database_api_assets", "get_assets",
    "database_api_objects", "get_objects"
)
@lcc.suite(
    "Check work of methods: 'get_assets', 'get_objects (asset & dynamic asset data & bitasset data objects)'",
    rank=1
)
class GetAssets(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.test(
        "Simple work of methods: 'get_assets', 'get_objects (asset & dynamic asset data)")
    def method_main_check(self):
        lcc.set_step("Get default asset of the chain")
        params = [self.echo_asset]
        response_id = self.send_request(self.get_request("get_assets", [params]),
                                        self.__database_api_identifier)
        get_assets_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_assets' with asset_ids='{}' parameter".format(params))

        lcc.set_step("Check simple work of method 'get_assets'")
        for i, asset_info in enumerate(get_assets_results):
            lcc.set_step("Checking asset object #{} - '{}'".format(i, params[i]))
            self.object_validator.validate_asset_object(self, asset_info)

        lcc.set_step("Get asset object")
        response_id = self.send_request(self.get_request("get_objects", [params]), self.__database_api_identifier)
        get_objects_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with params: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that(
            "'list of received objects'",
            get_objects_results, has_length(len(params)),
            quiet=True
        )

        lcc.set_step("Check the identity of returned results of api-methods: 'get_assets', 'get_objects'")
        require_that(
            'results',
            get_objects_results, equal_to(get_assets_results),
            quiet=True
        )

        lcc.set_step("Get asset dynamic data object")
        asset_dynamic_data_id = get_assets_results[0]["dynamic_asset_data_id"]
        params = [asset_dynamic_data_id]
        response_id = self.send_request(self.get_request("get_objects", [params]), self.__database_api_identifier)
        get_objects_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with params: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that(
            "'list of received objects'",
            get_objects_results, has_length(len(params)),
            quiet=True
        )
        for i, asset_dynamic_data in enumerate(get_objects_results):
            lcc.set_step("Checking dynamic asset data object #{} - '{}'".format(i, params[i]))
            lcc.log_info("{}".format(asset_dynamic_data))
            self.object_validator.validate_asset_dynamic_data_object(self, asset_dynamic_data)


@lcc.prop("positive", "type")
@lcc.tags(
    "api", "database_api", "database_api_assets", "get_assets",
    "database_api_objects", "get_objects"
)
@lcc.suite(
    "Positive testing of methods:'get_assets', 'get_objects (asset & dynamic asset data & bitasset data objects)'",
    rank=2
)
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

    @lcc.test("Get object for asset bitasset data")
    @lcc.depends_on("DatabaseApi.Assets.GetAssets.GetAssets.method_main_check")
    def get_object_for_asset_bitasset_data(self, get_random_valid_asset_name):
        new_asset_name = get_random_valid_asset_name

        lcc.set_step("Perform creating of bitasset")
        asset_create_operation = self.echo_ops.get_asset_create_operation(
            echo=self.echo,
            issuer=self.echo_acc0,
            symbol=new_asset_name,
            feed_lifetime_sec=86400,
            minimum_feeds=1,
            short_backing_asset=self.echo_asset
        )
        collected_operation = self.collect_operations(asset_create_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        created_asset_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Asset successfully created, id={}".format(created_asset_id))

        lcc.set_step("Get bitasset id from asset info")
        response_id = self.send_request(self.get_request("get_assets", [[created_asset_id]]),
                                        self.__database_api_identifier)
        created_asset = self.get_response(response_id)["result"][0]

        bitasset_id = created_asset["bitasset_data_id"]

        response_id = self.send_request(self.get_request("get_objects", [[bitasset_id]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]

        lcc.set_step("Check bitasset object")
        self.object_validator.validate_asset_bitasset_data_object(self, result)

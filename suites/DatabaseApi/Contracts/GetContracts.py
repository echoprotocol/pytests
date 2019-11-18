# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_str, is_false, check_that, has_length, require_that, \
    require_that_in, is_true, not_equal_to, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_contracts'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_contracts", "get_contracts")
@lcc.suite("Check work of method 'get_contracts'", rank=1)
class GetContracts(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")

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

    @lcc.test("Simple work of method 'get_contracts'")
    def method_main_check(self):
        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier,
                                                 supported_asset_id=self.echo_asset)

        lcc.set_step("Get info about created contract")
        response_id = self.send_request(self.get_request("get_contracts", [[contract_id]]),
                                        self.__database_api_identifier)
        results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_contracts' with param: '{}'".format(contract_id))

        lcc.set_step("Check simple work of method 'get_contracts'")
        result = results[0]
        self.object_validator.validate_contract_object(self, result)
        require_that_in(
            result,
            "destroyed", is_false(),
            "type", equal_to("evm"),
            "supported_asset_id", equal_to(self.echo_asset),
            "owner", equal_to(self.echo_acc0),
            quiet=True
        )


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_contracts", "get_contracts")
@lcc.suite("Positive testing of method 'get_contracts'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None
        self.contract_1 = self.get_byte_code("piggy", "code")
        self.break_piggy = self.get_byte_code("piggy", "breakPiggy()")
        self.contract_2 = self.get_byte_code("asset_int", "code")

    @staticmethod
    def check_contracts_ids(response, contracts):
        results = response["result"]
        if require_that("contracts info", results, has_length(len(contracts))):
            for i, result in enumerate(results):
                lcc.log_info("Check contract #{}:".format(i))
                require_that_in(
                    result,
                    ["id"], is_str(contracts[i]),
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
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Get info about two contracts")
    @lcc.depends_on("DatabaseApi.Contracts.GetContracts.GetContracts.method_main_check")
    def get_info_about_two_contracts(self):
        contracts = []

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_1, self.__database_api_identifier)
        contracts.append(contract_id)

        lcc.set_step("Get info about created contract")
        response_id = self.send_request(self.get_request("get_contracts", [contracts]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contracts' with param: '{}'".format(contracts))

        lcc.set_step("Check contract id of created contract")
        self.check_contracts_ids(response, contracts)

        lcc.set_step("Create 'asset_int' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_2, self.__database_api_identifier)
        contracts.append(contract_id)

        lcc.set_step("Get info about created contract")
        response_id = self.send_request(self.get_request("get_contracts", [contracts]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contracts' with params: '{}'".format(contracts))

        lcc.set_step("Check contract ids of two created contracts")
        self.check_contracts_ids(response, contracts)

    @lcc.test("Check work of destroyed field")
    @lcc.depends_on("DatabaseApi.Contracts.GetContracts.GetContracts.method_main_check")
    def check_destroyed_field(self):
        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_1, self.__database_api_identifier)

        lcc.set_step("Get info about created contract")
        response_id = self.send_request(self.get_request("get_contracts", [[contract_id]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contracts' with param: '{}'".format(contract_id))

        lcc.set_step("Check 'destroyed' field")
        result = response["result"][0]
        check_that(
            "'contract not destroyed'",
            result["destroyed"], is_false()
        )

        lcc.set_step("Destroy the contract. Call 'breakPiggy' method")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.break_piggy, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Call contract method 'breakPiggy' to destroy contract")

        lcc.set_step("Get updated info about created contract")
        response_id = self.send_request(self.get_request("get_contracts", [[contract_id]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contracts' with param: '{}'".format(contract_id))

        lcc.set_step("Check that contract to be 'destroyed=True'")
        result = response["result"][0]
        check_that(
            "'contract destroyed'",
            result["destroyed"], is_true()
        )

    @lcc.test("Check work of supported_asset_id field")
    @lcc.depends_on("DatabaseApi.Contracts.GetContracts.GetContracts.method_main_check")
    def check_supported_asset_id_field(self, get_random_valid_asset_name):
        asset_name = get_random_valid_asset_name

        lcc.set_step("Create asset and get id new asset")
        asset_id = self.utils.get_asset_id(self, asset_name, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(asset_id))

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        operation = self.echo_ops.get_contract_create_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                value_asset_id=asset_id, bytecode=self.contract_1,
                                                                supported_asset_id=asset_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_id = self.get_contract_id(contract_result)

        lcc.set_step("Get info about created contract")
        response_id = self.send_request(self.get_request("get_contracts", [[contract_id]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contracts' with param: '{}'".format(contract_id))

        lcc.set_step("Check that contract support expected asset_id")
        result = response["result"][0]
        check_that(
            "'contract supported_asset_id'",
            result["supported_asset_id"], is_str(asset_id)
        )

    @lcc.test("Check work of statistics field")
    @lcc.depends_on("DatabaseApi.Contracts.GetContracts.GetContracts.method_main_check")
    def check_statistics_field(self):
        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_1, self.__database_api_identifier)

        lcc.set_step("Get info about created contract. Store statistics_id")
        response_id = self.send_request(self.get_request("get_contracts", [[contract_id]]),
                                        self.__database_api_identifier)
        statistics_id = self.get_response(response_id)["result"][0]["statistics"]
        lcc.log_info("Contract '{}' has '{}' 'statistics_id'".format(contract_id, statistics_id))

        lcc.set_step("Call method 'get_objects' with stored statistics_id")
        response_id = self.send_request(self.get_request("get_objects", [[statistics_id]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_objects' with param: '{}'".format(statistics_id))

        lcc.set_step("Check that statistics show right 'owner' object")
        check_that(
            "'statistics_id'",
            response["result"][0]["owner"], is_str(contract_id)
        )

    @lcc.test("Check work of owner field")
    @lcc.depends_on("DatabaseApi.Contracts.GetContracts.GetContracts.method_main_check")
    def check_owner_field(self):
        creators = [self.echo_acc0, self.echo_acc1]

        lcc.set_step("Create two the same contracts in the Echo network and get their contract id")
        contract_id_1 = self.utils.get_contract_id(self, creators[0], self.contract_1,
                                                   self.__database_api_identifier)
        contract_id_2 = self.utils.get_contract_id(self, creators[1], self.contract_1,
                                                   self.__database_api_identifier)
        contracts_ids = [contract_id_1, contract_id_2]

        lcc.set_step("Get info about created contracts")
        response_id = self.send_request(self.get_request("get_contracts", [contracts_ids]),
                                        self.__database_api_identifier)
        contracts = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_contracts' with params: '{}'".format(contracts_ids))

        lcc.set_step("Check that the same contracts have different owners (creators)")
        for i, contract in enumerate(contracts):
            require_that(
                "'#{} contract owner'".format(str(i)),
                contract["owner"], is_str(creators[i])
            )

        check_that(
            "'contract owners'",
            contracts[0]["owner"], not_equal_to(contracts[1]["owner"])
        )

# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import has_length, require_that, require_that_in, equal_to

from common.base_test import BaseTest
SUITE = {
    "description": "Method 'get_objects' (contract result object)"
}


@lcc.prop("main", "type")
@lcc.tags("api", "database_api", "database_api_objects", "get_objects", "aaa")
@lcc.suite("Check work of method 'get_objects' (contract result object)", rank=1)
class GetContractResultObjects(BaseTest):

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

    @lcc.test("Simple work of method 'get_objects' (contract result object)")
    def method_main_check(self):
        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_info = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier,
                                                   supported_asset_id=self.echo_asset, need_broadcast_result=True)
        contract_id = contract_info["contract_id"]
        contract_result_id = contract_info["broadcast_result"]["trx"]["operation_results"][0][1]

        lcc.set_step("Get contract result object")
        params = [contract_result_id]
        response_id = self.send_request(self.get_request("get_objects", [params]),
                                        self.__database_api_identifier)
        results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with param: '{}'".format(contract_id))

        lcc.set_step("Check length of received objects")
        require_that(
            "'list of received objects'",
            results,
            has_length(len(params)),
            quiet=True
        )

        for i, result in enumerate(results):
            lcc.set_step("Checking contract result object #{} - '{}'".format(i, params[i]))
            self.object_validator.validate_contract_result_object(self, result)
            require_that_in(
                result,
                "id", equal_to(contract_result_id),
                "type", equal_to("evm"),
                "contracts_id", equal_to([contract_id]),
                quiet=True
            )

# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_dict, is_integer, is_, require_that, check_that

from common.base_test import BaseTest

SUITE = {
    "description": "Scenario 'Create new asset and  get required fees for contact operation'"
}


@lcc.prop("main", "type")
@lcc.tags("scenarios", "required_fee_of_contract_operation_with_new_asset")
@lcc.suite("Check scenario 'required_fee_of_contract_operation_with_new_asset'", rank=1)
class RequiredFeeOfContractOperationWithNewAsset(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")

    def get_required_fees(self, operations, asset, negative=False):
        params = [[operations], asset]
        response_id = self.send_request(self.get_request("get_required_fees", params), self.__database_api_identifier)
        return self.get_response(response_id, negative=negative)

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
        lcc.log_info(
            "Echo account is {}''".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Scenario 'check new asset in required fee of contract operation'")
    def required_fee_of_contract_operation_with_new_asset(self, get_random_valid_asset_name):
        lcc.set_step("Generate assets symbol")
        asset_symbol = get_random_valid_asset_name
        lcc.log_info('Generated asset names: {}'.format(asset_symbol))

        lcc.set_step("Perform assets creation operation")
        asset_id = self.utils.get_asset_id(self, asset_symbol,
                                           self.__database_api_identifier,
                                           need_operation=True)[0]
        lcc.log_info("Assets was created, ids='{}'".format(asset_id))

        lcc.set_step("First: Collect operation for deploying contract")
        operation = self.echo_ops.get_contract_create_operation(self.echo, self.echo_acc0, self.contract,
                                                                self.__database_api_identifier)
        first_operation = self.collect_operations(operation, self.__database_api_identifier, debug_mode=True)

        lcc.set_step("Second: Collect operation for calling contract method")
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=operation, log_broadcast=False)
        contract_result = self.get_operation_results_ids(broadcast_result)
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result]),
                                        self.__database_api_identifier)
        response = self.get_trx_completed_response(response_id)
        contract_id = self.get_contract_id(response)
        second_operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                     bytecode=self.greet, callee=contract_id,
                                                                     debug_mode=True)

        lcc.set_step("Check method 'get_required_fees' for deploying contact operation ")
        params = [[first_operation], asset_id]
        response_id = self.send_request(self.get_request("get_required_fees", params), self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]
        require_that("'fee'", result, is_dict())
        check_that("'amount'", result["amount"], is_integer())
        check_that("'asset_id'", result["asset_id"], is_(asset_id))

        lcc.set_step("Check method 'get_required_fees' for call contact method operation")
        params = [[second_operation], asset_id]
        response_id = self.send_request(self.get_request("get_required_fees", params), self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]
        require_that("'result'", result, is_dict())
        fee = result["fee"]
        require_that("'fee'", fee, is_dict())
        check_that("'asset_id'", fee["asset_id"], is_(asset_id))
        check_that("'amount'", fee["amount"], is_integer())
        user_to_pay = result["user_to_pay"]
        require_that("'user_to_pay'", user_to_pay, is_dict())
        check_that("'asset_id'", user_to_pay["asset_id"], is_(asset_id))
        check_that("'amount'", user_to_pay["amount"], is_integer())

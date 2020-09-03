# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'asset_claim_fees'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "asset_management_operations", "asset_claim_fees")
@lcc.suite("Check work of method 'asset_claim_fees'", rank=1)
class AssetClaimFees(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

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
        lcc.log_info("Echo accounts are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'asset_claim_fees'")
    def method_main_check(self, get_random_valid_account_name, get_random_valid_asset_name,
                          get_random_integer_up_to_ten):
        new_account = get_random_valid_account_name
        new_asset_name = get_random_valid_asset_name
        transfer_operation_count = get_random_integer_up_to_ten

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Create a new asset and get new asset_id")
        new_asset_id = self.utils.get_asset_id(self, new_asset_name, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id: '{}'".format(new_asset_id))

        lcc.set_step("Add new asset to new account")
        asset_issue_operation = self.echo_ops.get_asset_issue_operation(echo=self.echo, issuer=self.echo_acc0,
                                                                        value_amount=1000, value_asset_id=new_asset_id,
                                                                        issue_to_account=new_account)
        collected_operation = self.collect_operations(asset_issue_operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("New asset: '{}' added to new account: '{}'".format(new_account, new_asset_id))
        lcc.set_step("Broadcast transfer operation to increase 'accumulated_fees' amount")
        collected_operation = []

        lcc.set_step("Perform 'asset_fund_fee_pool_operation'")
        asset_fund_fee_pool_operation = self.echo_ops.get_asset_fund_fee_pool_operation(
            self.echo, from_account=self.echo_acc0, asset_id=new_asset_id, amount=1000)
        collected_op = self.collect_operations(asset_fund_fee_pool_operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_op,
                                log_broadcast=False)
        lcc.log_info("'asset_fund_fee_pool_operation' broadcasted successfully")

        self.utils.perform_transfer_operations(self, self.echo_acc0, new_account, self.__database_api_identifier,
                                               transfer_amount=20)
        operation = self.echo_ops.get_transfer_operation(
            echo=self.echo, from_account_id=new_account,
            to_account_id=self.echo_acc0, amount=1, fee_amount=20,
            fee_asset_id=new_asset_id, amount_asset_id=new_asset_id)
        fee = self.get_required_fee(operation, self.__database_api_identifier)["amount"]
        for i in range(transfer_operation_count):
            collected_operation.append(self.collect_operations(operation, self.__database_api_identifier,
                                                               fee_amount=20, fee_asset_id=new_asset_id))
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("transfer operation broadcasted {} times".format(transfer_operation_count))

        lcc.set_step("Check that accumulated_fees increased")
        fee = 20
        claim_amount = fee * transfer_operation_count
        response_id = self.send_request(self.get_request("get_objects", [[new_asset_id]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]["dynamic_asset_data_id"]
        response_id = self.send_request(self.get_request("get_objects", [[result]]),
                                        self.__database_api_identifier)
        fee_pool = self.get_response(response_id)["result"][0]["accumulated_fees"]
        check_that("accumulated_fees", fee_pool, equal_to(claim_amount))

        lcc.set_step("Perform claim fees operation")
        asset_claim_fees_operation = self.echo_ops.get_asset_claim_fees_operation(
            self.echo, issuer=self.echo_acc0, claim_amount=claim_amount,
            claim_asset_id=new_asset_id
        )
        collected_operation = self.collect_operations(asset_claim_fees_operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("Fees claimed")

        lcc.set_step("Check that fees claimed successfully")
        response_id = self.send_request(self.get_request("get_objects", [[new_asset_id]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]["dynamic_asset_data_id"]
        response_id = self.send_request(self.get_request("get_objects", [[result]]),
                                        self.__database_api_identifier)
        fee_pool = self.get_response(response_id)["result"][0]["accumulated_fees"]
        check_that("accumulated_fees", fee_pool, equal_to(0))

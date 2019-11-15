# -*- coding: utf-8 -*-
import json
import os
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_
from project import UTILS, INIT4_PK
from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'balance_claim'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "asset_transfer_operations", "balance_claim")
@lcc.suite("Check work of method 'balance_claim'", rank=1)
class BalanceClaim(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.init4_account_name = "init4"

    def check_status_file(self):
        if not os.path.exists(UTILS):
            with open(UTILS, "w") as utils:
                utils_data = {"balance_claim_operation": {"state": True}}
                utils.write(json.dumps(utils_data))
        else:
            with open(UTILS, "r") as utils:
                utils_data = json.load(utils)
                if "balance_claim_operation" not in utils_data:
                    utils_data.update({"balance_claim_operation": {"state": True}})
                    with open(UTILS, "w") as utils:
                        utils.write(json.dumps(utils_data))

        self.state = utils_data["balance_claim_operation"]["state"]

    def change_test_status(self):
        execution_status = json.load(open(UTILS, "r"))
        if execution_status["balance_claim_operation"]:
            execution_status["balance_claim_operation"]["state"] = False
            self.state = False
            with open(UTILS, "w") as file:
                file.write(json.dumps(execution_status))
        else:
            self.state = False

    @staticmethod
    def add_log_info(log):
        execution_status = json.load(open(UTILS, "r"))
        execution_status["balance_claim_operation"]["state"] = False
        with open(UTILS, "w") as file:
            execution_status["balance_claim_operation"].update({"passed": log})
            file.write(json.dumps(execution_status))

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        if self.utils.check_accounts_have_initial_balances([self.init4_account_name]):
                lcc.set_step("Check execution status")
                self.check_status_file()
                if self.state:
                    lcc.set_step("Setup for {}".format(self.__class__.__name__))
                    self.__database_api_identifier = self.get_identifier("database")
                    lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
                    self.public_key = self.get_account_by_name(self.init4_account_name,
                                                               self.__database_api_identifier)["result"]["echorand_key"]
                    lcc.log_info("'{}' account public key: '{}'".format(self.init4_account_name, self.public_key))
        else:
            lcc.log_error("'{}' account does not have initial balance in genesis".format(self.init4_account_name))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'balance_claim'")
    def method_main_check(self, get_random_valid_account_name):
        if self.state:
            account_info = self.get_account_by_name(self.init4_account_name, self.__database_api_identifier)
            account_id = account_info["result"]["id"]
            public_key = account_info["result"]["echorand_key"]
            lcc.log_info(
                "'{}' account has id='{}' and public_key='{}'".format(self.init4_account_name, account_id,
                                                                      public_key))

            lcc.set_step("Get balance objects before balance claim operation. Store balance id and amount")
            response_id = self.send_request(self.get_request("get_balance_objects", [[public_key]]),
                                            self.__database_api_identifier)
            result = self.get_response(response_id)["result"][0]
            lcc.log_info("Call method 'get_balance_objects' with param: '{}'".format(public_key))
            balance_id = result["id"]
            balance_amount = int(result["balance"]["amount"])
            lcc.log_info(
                "'{}' account has balance with id='{}' and amount='{}'".format(self.init4_account_name, balance_id,
                                                                               balance_amount))
            lcc.set_step("Perform 'balance_claim_operation'")
            operation = self.echo_ops.get_balance_claim_operation(echo=self.echo, deposit_to_account=account_id,
                                                                  balance_owner_public_key=public_key,
                                                                  value_amount=balance_amount,
                                                                  balance_owner_private_key=INIT4_PK,
                                                                  balance_to_claim=balance_id)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
            if self.is_operation_completed(broadcast_result, expected_static_variant=0):
                lcc.log_info("Balance claimed succesfully")
                self.change_test_status()

            lcc.set_step("Get balance objects after balance claim operation")
            response_id = self.send_request(self.get_request("get_balance_objects", [[public_key]]),
                                            self.__database_api_identifier)
            self.add_log_info(False)
            result = self.get_response(response_id)["result"]
            lcc.log_info("Call method 'get_balance_objects' with param: '{}'".format(public_key))

            lcc.set_step("Check response from 'get_balance_objects' method after balance claim operation")
            if check_that("balance", result, is_([])):
                self.add_log_info(True)
        else:
            execution_status = json.load(open(UTILS, "r"))["balance_claim_operation"]
            if execution_status["passed"]:
                lcc.log_info("Testing of the 'balance_claim_operation' method was successfully completed earlier")
            else:
                lcc.log_error("Test of method 'balance_claim_operation' failed during the previous run. "
                              "Can not claim initial balance again. To run test again please run a clean node.")

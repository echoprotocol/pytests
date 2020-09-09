# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Operation 'contract_update'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "contract_operations", "contract_update")
@lcc.suite("Check work of method 'contract_update'", rank=1)
class ContractUpdate(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.echo_acc0 = None
        self.echo_acc1 = None

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
        self.echo_acc1 = self.get_account_id(
            self.accounts[1], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'contract_update'")
    def method_main_check(self, get_random_integer):
        lcc.set_step("Create 'Piggy' contract in the Echo network and check operation in transaction")
        operation = self.echo_ops.get_contract_create_operation(
            echo=self.echo,
            registrar=self.echo_acc0,
            bytecode=self.piggy_contract,
            value_amount=10,
            value_asset_id=self.echo_asset
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_id = self.get_contract_id(contract_result)
        lcc.log_info("'contract_create' operation broadcasted successfully, contract_id: '{}'".format(contract_id))

        lcc.set_step("Perform 'contract_update' operation")
        operation = self.echo_ops.get_contract_update_operation(
            echo=self.echo, sender=self.echo_acc0, contract=contract_id, new_owner=self.echo_acc1
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("'contract_update' operation broadcasted successfully")

        lcc.set_step("Check that contract owner correct")
        response_id = self.send_request(
            self.get_request("get_contracts", [[contract_id]]), self.__database_api_identifier
        )
        owner = self.get_response(response_id)["result"][0]["owner"]
        check_that("owner", owner, equal_to(self.echo_acc1))

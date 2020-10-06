# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT4_PK

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'create_contract'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_contracts", "wallet_create_contract")
@lcc.suite("Check work of method 'create_contract'", rank=1)
class CreateContract(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
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
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        self.init4 = self.get_account_id(
            'init4', self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo accounts are: #1 = '{}', #2 = '{}'".format(self.echo_acc0, self.init4))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_create_contract'")
    def method_main_check(self):
        self.unlock_wallet()
        lcc.set_step("Import key")
        self.send_wallet_request("import_key", ['init4', INIT4_PK], log_response=False)
        lcc.log_info("Key imported")

        lcc.set_step("Сheck create_contract method")
        response = self.send_wallet_request("create_contract", [self.init4, self.contract, 1, self.echo_asset, "", True], log_response=False)['result']
        check_that("contract code", response['operations'][0][1]['code'], equal_to(self.contract), quiet=True)

        lcc.set_step("Create 'Piggy' contract in the Echo network")
        operation = self.echo_ops.get_contract_create_operation(
            echo=self.echo,
            registrar=self.echo_acc0,
            bytecode=self.contract,
            value_amount=1,
            value_asset_id=self.echo_asset
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("Contract created successfully")
        lcc.set_step("Check that field of contract create operation are equal")
        check_that('create_contract result fields', list(response['operations'][0][1].keys()), equal_to(list(broadcast_result['trx']['operations'][0][1].keys())), quiet=True)

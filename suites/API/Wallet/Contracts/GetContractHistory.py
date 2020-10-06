# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_str

SUITE = {
    "description": "Method 'get_contract_history'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_contracts", "wallet_get_contract_history")
@lcc.suite("Check work of method 'get_contract_history'", rank=1)
class GetContractHistory(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.valid_contract_id = None

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
        lcc.log_info("Echo account are: '{}'".format(self.echo_acc0))
        self.valid_contract_id = self.utils.get_contract_id(
            self, self.echo_acc0, self.contract, self.__database_api_identifier
        )

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_contract_history'")
    def method_main_check(self):
        lcc.set_step("Сheck get_contract_history method")
        response = self.send_wallet_request(
            "get_contract_history", [self.valid_contract_id, 1], log_response=False
        )['result']
        check_that("description", response[0]['description'], is_str())
        self.object_validator.validate_operation_history_object(self, response[0]['op'])

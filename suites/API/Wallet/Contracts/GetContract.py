# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_, is_list, require_that

SUITE = {
    "description": "Method 'get_contract'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_contracts", "wallet_get_contract")
@lcc.suite("Check work of method 'get_contract'", rank=1)
class GetContract(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_get_contract'")
    def method_main_check(self):
        lcc.set_step("Сheck get_contract method")
        response = self.send_wallet_request("get_contract", [self.valid_contract_id], log_response=False)
        contract_type = response["result"][0]
        require_that("contract index", contract_type, is_(0))
        contract_info = response["result"][1]
        if not self.type_validator.is_hex(contract_info["code"]):
            lcc.log_error("Wrong format of 'code', got: {}".format(contract_info["code"]))
        else:
            lcc.log_info("'code' has correct format: hex")

        contract_storage = contract_info["storage"]
        if not self.type_validator.is_hex(contract_storage[0][0]):
            lcc.log_error("Wrong format of 'contract storage var 1', got: {}".format(contract_storage[0][0]))
        else:
            lcc.log_info("'contract storage var 1' has correct format: hex")
        check_that("'contract storage var 2'", contract_storage[0][1], is_list(), quiet=True)

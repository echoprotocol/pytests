# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import equal_to, require_that

SUITE = {
    "description": "Method 'get_evm_addresses'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_get_evm_addresses")
@lcc.suite("Check work of method 'get_evm_addresses'", rank=1)
class GetEvmAddresses(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
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
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_evm_addresses'")
    def method_main_check(self, get_random_eth_address):
        evm_address = get_random_eth_address

        lcc.set_step("Register EVM address for account")
        operation = self.echo_ops.get_evm_address_register_operation(
            echo=self.echo, account=self.echo_acc0, evm_address=evm_address
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Error: can't register evm address, response:\n{}".format(broadcast_result))
        operation_result = broadcast_result["trx"]["operation_results"][0][1]
        lcc.log_info("EVM address registred successfully")

        lcc.set_step("Get EVM address of {} account".format(self.echo_acc0))
        response = self.send_wallet_request("get_evm_addresses", [self.echo_acc0], log_response=True)
        account_evm_address = response['result'][-1]["evm_address"]

        response_id = self.send_request(
            self.get_request("get_objects", [[operation_result]]), self.__database_api_identifier
        )
        evm_address_object = self.get_response(response_id)["result"][0]["evm_address"]
        require_that("evm_address", account_evm_address, equal_to(evm_address_object))

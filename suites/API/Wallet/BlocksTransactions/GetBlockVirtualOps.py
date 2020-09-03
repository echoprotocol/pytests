# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from lemoncheesecake.matching import require_that, has_entry, is_not_none, check_that, equal_to

from common.wallet_base_test import WalletBaseTest
from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_block_virtual_ops'"
}


@lcc.prop("main", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "wallet_api", "wallet_get_block_ops")
@lcc.suite("Check work of method 'get_block_ops'", rank=1)
class GetBlockVirtualOps(BaseTest, WalletBaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.contract = self.get_byte_code("piggy", "code")
        self.get_pennie = self.get_byte_code("piggy", "pennieReturned()")

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
        self.contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract,
                                                      self.__database_api_identifier)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_block_virtual_ops'")
    def method_main_check(self):
        contract_internal_call_operation_id = 34

        lcc.set_step("Call virtual 'contract_internal_call_operation' in ECHO network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract,
                                                 self.__database_api_identifier, value_amount=10)
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.get_pennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        block_num = broadcast_result["block_num"]
        lcc.log_info("Block number with operations is {}".format(block_num))

        lcc.set_step("Call method 'get_block_virtual_ops'")
        self.produce_block(self.__database_api_identifier)
        response = self.send_wallet_request("get_block_virtual_ops", [block_num])
        require_that("'result'", response["result"], is_not_none(), quiet=True)
        require_that("'operation id'", response["result"][0]["op"][0], equal_to(contract_internal_call_operation_id),
                     quiet=True)


@lcc.prop("negative", "type")
@lcc.tags("api", "wallet_api", "wallet_get_block_ops")
@lcc.suite("Negative testing of method 'get_block_virtual_ops'", rank=3)
class NegativeTesting(WalletBaseTest):

    @lcc.prop("type", "method")
    @lcc.test("Call method with params of all types")
    @lcc.depends_on("API.Wallet.BlocksTransactions.GetBlockVirtualOps.GetBlockVirtualOps.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            if i == 4:
                continue
            response = self.send_wallet_request("get_block_virtual_ops", random_values[i], negative=True)
            check_that(
                "'get_account_count' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True
            )

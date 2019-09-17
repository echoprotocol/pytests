# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_true, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Check calculation of total fees of processed transaction"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("fees_collected_in_processed_transaction")
@lcc.suite("Check scenario 'fees_collected_in_processed_transaction'")
class FeesCollectedInProcessedTransaction(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

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
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Scenario 'fees_collected_in_processed_transaction'")
    def fees_collected_in_processed_transaction(self):
        lcc.set_step("Collect first 'transfer_operation' operation")
        first_transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                        from_account_id=self.echo_acc0,
                                                                        to_account_id=self.echo_acc1)
        collected_first_transfer_operation = self.collect_operations(first_transfer_operation,
                                                                     self.__database_api_identifier)
        lcc.log_info("Transfer operation: '{}'".format(str(first_transfer_operation)))

        lcc.set_step("Collect second 'transfer_operation' operation")
        second_transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                         from_account_id=self.echo_acc0,
                                                                         to_account_id=self.echo_acc1)
        collected_second_transfer_operation = self.collect_operations(second_transfer_operation,
                                                                      self.__database_api_identifier)
        lcc.log_info("Transfer operation: '{}'".format(str(second_transfer_operation)))

        lcc.set_step("Broadcast transaction that contains simple transfer operation to the ECHO network")
        collected_operations = [collected_first_transfer_operation, collected_second_transfer_operation]
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operations,
                                                   log_broadcast=False)
        require_that(
            "broadcast transaction complete successfully",
            self.is_operation_completed(broadcast_result, 0), is_true(), quiet=True)

        lcc.set_step("Check 'fees_collected' amount in broadcast")
        operations_fees = 0
        operations_from_broadcast_result = broadcast_result["trx"]["operations"]
        for operation in operations_from_broadcast_result:
            operations_fees += operation[1]["fee"]["amount"]
        require_that("'fees_collected'", broadcast_result["trx"]["fees_collected"], equal_to(operations_fees),
                     quiet=True)

        lcc.set_step("Get transaction by method 'get_transaction'")
        broadcast_transaction_block_num = broadcast_result["block_num"]
        broadcast_transaction_num = broadcast_result["trx_num"]
        params = [broadcast_transaction_block_num, broadcast_transaction_num]
        response_id = self.send_request(self.get_request("get_transaction", params),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_transaction' with block_num='{}', trx_num='{}' parameters".format(
            broadcast_transaction_block_num, broadcast_transaction_num))

        lcc.set_step("Check 'fees_collected' amount in method's result 'get_transaction'")
        operations_fees = 0
        operations_from_response = result["operations"]
        for operation in operations_from_response:
            operations_fees += operation[1]["fee"]["amount"]
        require_that("'fees_collected'", result["fees_collected"], equal_to(operations_fees),
                     quiet=True)
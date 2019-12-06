# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, check_that_in, is_str, is_list, is_integer, check_that, equal_to, \
    has_length, is_true

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_block'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_blocks_transactions", "get_block")
@lcc.suite("Check work of method 'get_block'", rank=1)
class GetBlock(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_block'")
    def method_main_check(self):
        lcc.set_step("Get the full first block in the chain")
        block_num = 1
        response_id = self.send_request(self.get_request("get_block", [block_num]), self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_block' with block_num='{}' parameter".format(block_num))

        lcc.set_step("Check simple work of method 'get_block'")
        block_header = response["result"]
        require_that(
            "'the first full block'",
            block_header, has_length(14)
        )
        if not self.type_validator.is_iso8601(block_header["timestamp"]):
            lcc.log_error("Wrong format of 'timestamp', got: {}".format(block_header["timestamp"]))
        else:
            lcc.log_info("'timestamp' has correct format: iso8601")
        if not self.type_validator.is_account_id(block_header["account"]):
            lcc.log_error("Wrong format of 'account id', got: {}".format(block_header["account"]))
        else:
            lcc.log_info("'id' has correct format: account_id")
        if not self.type_validator.is_account_id(block_header["delegate"]):
            lcc.log_error("Wrong format of 'delegate', got: {}".format(block_header["delegate"]))
        else:
            lcc.log_info("'delegate' has correct format: account_id")
        check_that_in(
            block_header,
            "previous", is_str("0000000000000000000000000000000000000000"),
            "round", is_integer(),
            "attempt", is_integer(),
            "transaction_merkle_root", is_str("0000000000000000000000000000000000000000"),
            "vm_root", is_list(),
            "prev_signatures", is_list(),
            "extensions", is_list(),
            "ed_signature", is_str(),
            "rand", is_str(),
            "cert", is_list(),
            "transactions", is_list(),
            quiet=True
        )

        certificates = block_header["cert"]
        for i, certificate in enumerate(certificates):
            lcc.log_info("Check fields in certificate#'{}'".format(i))
            check_that_in(
                certificate,
                "_step", is_integer(),
                "_value", is_integer(),
                "_producer", is_integer(),
                "_delegate", is_integer(),
                "_fallback", is_integer(),
                quiet=False
            )
        if not self.type_validator.is_digit(certificate["_leader"]):
            lcc.log_error("Wrong format of '_leader', got: {}".format(certificate["_leader"]))
        else:
            lcc.log_info("'_leader' has correct format: int")


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_blocks_transactions", "get_block")
@lcc.suite("Positive testing of method 'get_block'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

    def compare_objects(self, first_field, second_field, key=None):
        if isinstance(first_field, (list, dict)):
            if isinstance(first_field, list) and len(first_field):
                for key, elem in enumerate(first_field):
                    self.compare_objects(elem, second_field[key])
            elif isinstance(first_field, dict) and len(first_field):
                for key in list(first_field.keys()):
                    self.compare_objects(first_field[key], second_field[key], key)
        else:
            description = "list element"
            if key:
                description = "'{}'".format(key)
            check_that("{}".format(description), first_field, equal_to(second_field), quiet=True)

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

    @lcc.test("Broadcast transaction and check info about it in block")
    @lcc.depends_on("DatabaseApi.BlocksTransactions.GetBlock.GetBlock.method_main_check")
    def check_transaction_info_in_block(self):
        lcc.set_step("Collect 'get_transaction' operation")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo, from_account_id=self.echo_acc0,
                                                                  to_account_id=self.echo_acc1, amount=5)
        lcc.log_info("Transfer operation: '{}'".format(str(transfer_operation)))

        lcc.set_step("Broadcast transaction that contains simple transfer operation to the ECHO network")
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        require_that(
            "broadcast transaction complete successfully",
            self.is_operation_completed(broadcast_result, 0), is_true(), quiet=True
        )

        lcc.set_step("Get block, that contains transaction")
        broadcast_transaction_block_num = broadcast_result["block_num"]
        response_id = self.send_request(self.get_request("get_block", [broadcast_transaction_block_num]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_block' with block_num='{}' parameter".format(broadcast_transaction_block_num))

        lcc.set_step("Compare transaction objects (broadcast_result, 'get_block' method)")
        transaction_from_broadcast_result = broadcast_result["trx"]
        transactions_from_api_method = response["result"]["transactions"]
        for tx in transactions_from_api_method:
            if tx['signatures'] == transaction_from_broadcast_result["signatures"]:
                transaction_from_api_method = tx
                break

        require_that(
            "'transaction from broadcast result'",
            transaction_from_broadcast_result, has_length(9)
        )
        require_that(
            "'transaction from 'get_block' method result'",
            transaction_from_api_method, has_length(9)
        )
        self.compare_objects(transaction_from_broadcast_result, transaction_from_api_method)


@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_blocks_transactions", "get_block")
@lcc.suite("Negative testing of method 'get_block'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info(
            "API identifier are: database='{}'".format(self.__database_api_identifier))


    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Check negative int value in get_block")
    @lcc.depends_on("DatabaseApi.BlocksTransactions.GetBlock.GetBlock.method_main_check")
    def check_negative_int_value_in_get_block(self):
        error_message = "Assert Exception: result >= 0: Invalid cast from negative number to unsigned"

        lcc.set_step("Get 'get_block' with negative block number")
        response_id = self.send_request(self.get_request("get_block", [-1]),
                                        self.__database_api_identifier)
        message = self.get_response(response_id, negative=True)["error"]["message"]
        check_that(
            "error_message",
            message, equal_to(error_message),
            quiet=True
        )

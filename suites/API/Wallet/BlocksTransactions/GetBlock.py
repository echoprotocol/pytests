# -*- coding: utf-8 -*-
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import (
    check_that, check_that_in, has_entry, has_length, is_integer, is_list, is_not_none, is_str, require_that
)

SUITE = {
    "description": "Method 'get_block'"
}


@lcc.prop("main", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "wallet_api", "wallet_get_block")
@lcc.suite("Check work of method 'get_block'", rank=1)
class GetBlock(WalletBaseTest):

    def __init__(self):
        super().__init__()

    @lcc.test("Simple work of method 'get_block'")
    def method_main_check(self):
        lcc.set_step("Call method 'get_block'")
        response = self.send_wallet_request("get_block", ["0"])
        require_that("'result'", response["result"], is_not_none(), quiet=True)

        lcc.set_step("Check simple work of method 'get_block'")
        block_header = response["result"]
        require_that("'the first full block'", block_header, has_length(17))
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
        if not self.type_validator.is_hex(block_header["block_id"]):
            lcc.log_error("Wrong format of 'block_id', got: {}".format(block_header["block_id"]))
        else:
            lcc.log_info("'block_id' has correct format: hex")
        if not self.type_validator.is_echorand_key(block_header["signing_key"]):
            lcc.log_error("Wrong format of 'signing_key', got: {}".format(block_header["signing_key"]))
        else:
            lcc.log_info("'signing_key' has correct format: public_key")
        check_that_in(
            block_header,
            "previous",
            is_str("0000000000000000000000000000000000000000"),
            "round",
            is_integer(),
            "attempt",
            is_integer(),
            "transaction_merkle_root",
            is_str("0000000000000000000000000000000000000000"),
            "vm_root",
            is_list(),
            "prev_signatures",
            is_list(),
            "extensions",
            is_list(),
            "rand",
            is_str(),
            "cert",
            is_list(),
            "transactions",
            is_list(),
            "invalid_trx_ids",
            is_list(),
            "transaction_ids",
            is_list(),
            quiet=True
        )

        certificates = block_header["cert"]
        for i, certificate in enumerate(certificates):
            lcc.log_info("Check fields in certificate#'{}'".format(i))
            check_that_in(
                certificate,
                "_step",
                is_integer(),
                "_value",
                is_integer(),
                "_producer",
                is_integer(),
                "_delegate",
                is_integer(),
                "_fallback",
                is_integer(),
                quiet=False
            )
            if not self.type_validator.is_digit(certificate["_leader"]):
                lcc.log_error("Wrong format of '_leader', got: {}".format(certificate["_leader"]))
            else:
                lcc.log_info("'_leader' has correct format: int")


@lcc.prop("negative", "type")
@lcc.tags("api", "wallet_api", "wallet_get_block")
@lcc.suite("Negative testing of method 'get_block'", rank=3)
class NegativeTesting(WalletBaseTest):

    @lcc.prop("type", "method")
    @lcc.test("Call method with params of all types")
    @lcc.depends_on("API.Wallet.BlocksTransactions.GetBlock.GetBlock.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            if i == 4:
                continue
            response = self.send_wallet_request("get_block", random_values[i], negative=True)
            check_that(
                "'get_account_count' return error message with '{}' params".format(random_type_names[i]),
                response,
                has_entry("error"),
                quiet=True
            )

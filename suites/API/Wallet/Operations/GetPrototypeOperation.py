# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import equal_to, require_that

SUITE = {
    "description": "Method 'get_prototype_operation'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_operations", "wallet_get_prototype_operation")
@lcc.suite("Check work of method 'get_prototype_operation'", rank=1)
class GetPrototypeOperation(BaseTest, WalletBaseTest):

    def __init__(self):
        super().__init__()

    @lcc.test("Simple work of method 'get_prototype_operation'")
    def method_main_check(self):
        lcc.set_step("Make template transfer operation")
        transfer_operation = self.echo_ops.get_transfer_operation(
            echo=self.echo,
            from_account_id="1.2.0",
            to_account_id="1.2.0",
            amount=0,
            fee_amount=0,
            fee_asset_id="1.3.0",
            amount_asset_id="1.3.0"
        )[:2]
        lcc.log_info("Templa transfer operation: {}".format(transfer_operation))

        lcc.set_step("Call method 'get_object'")
        response = self.send_wallet_request("get_prototype_operation", ['transfer_operation'], log_response=True)

        lcc.set_step("Compare created transfer operation with received prototype")
        require_that(
            "Received transfer operation prototype", response["result"], equal_to(transfer_operation), quiet=True
        )

# -*- coding: utf-8 -*-
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, has_entry, is_not_none, require_that

from project import SECOND_NODE_IP

SUITE = {
    "description": "Method 'network_add_nodes'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "wallet_api", "wallet_objects", "wallet_network_add_nodes")
@lcc.suite("Check work of method 'network_add_nodes'", rank=1)
class NetworkAddNodes(WalletBaseTest):

    def __init__(self):
        super().__init__()

    @lcc.test("Simple work of method 'network_add_nodes'")
    def method_main_check(self):
        lcc.set_step("Call method 'network_add_nodes'")
        response = self.send_wallet_request("network_add_nodes", [[SECOND_NODE_IP]], debug_mode=True, log_response=True)
        # require_that("'result'", response["result"], is_not_none(), quiet=False)
        response = self.send_wallet_request("network_get_connected_peers", [], debug_mode=True, log_response=True)
        

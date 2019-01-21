# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from common.base_test import BaseTest

SUITE = {
    "description": "Test 'Piggy'"
}


@lcc.suite("Test smart contract")
@lcc.disabled()
class TestSmartContract(BaseTest):

    def __init__(self):
        super().__init__()
        self.__resp = None
        self.__id_net_broad = self.get_identifier(self._network_broadcast_api)
        self.__id_history = self.get_identifier(self._history_api)

    @lcc.test("")
    def test_piggy_smart_contract(self):
        pass

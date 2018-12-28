import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, contains_string

from common.utils import BaseTest

SUITE = {
    "description": "Test 'Network broadcast API'"
}


@lcc.suite("Test network broadcast methods")
class TestNetworkBroadcastMethod(BaseTest):
    __broadcast_block = "broadcast_block"
    __get_block_exp = "block_exp"
    __broadcast_transaction = "broadcast_transaction"
    __get_transaction_exp = "transaction_exp"

    def __init__(self):
        super().__init__()
        self.__resp = None
        self.__identifier = self.get_identifier(self._network_broadcast_api)

    @lcc.test("Broadcast block")
    @lcc.tags("don't work")
    def test_broadcast_block(self):
        lcc.set_step("Retrieve broadcast block")
        self.send_request(self.get_request(self.__broadcast_block,
                                           [self.get_expected(self.__get_block_exp)]),
                          self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Response")
        check_that(
            "'error message'",
            self.__resp["error"]["message"],
            contains_string("Assert Exception: item->num > std::max<int64_t>( 0, int64_t(_head->num) - "
                            "(_max_size) ): attempting to push a block that is too old")
        )

    @lcc.test("Broadcast transaction")
    @lcc.tags("don't work")
    def test_broadcast_transaction(self):
        lcc.set_step("Retrieve broadcast transaction")
        self.send_request(self.get_request(self.__broadcast_transaction,
                                           [self.get_expected(self.__get_transaction_exp)]),
                          self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Response")
        check_that(
            "'error message'",
            self.__resp["error"]["message"],
            contains_string("Assert Exception: trx.ref_block_prefix == tapos_block_summary.block_id._hash[1]: ")
        )

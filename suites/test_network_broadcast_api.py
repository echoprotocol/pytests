import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, contains_string

from common.utils import BaseTest

SUITE = {
    "description": "Test 'Network broadcast API'"
}


@lcc.suite("Test network broadcast methods")
class TestNetworkBroadcastMethod(BaseTest):
    broadcast_transaction = "broadcast_transaction"
    broadcast_params = "broadcast_params"

    def __init__(self):
        super().__init__()
        self.__resp = None

    def setup_test(self, test):
        # Get network_broadcast api identifier
        self.get_identifier(self._network_broadcast_api)

    @lcc.test("broadcast_transaction")
    def test_broadcast_transaction(self):
        """
        Try to send objects as a parameter
        """
        lcc.set_step("Retrieve broadcast_transaction.")
        self.send_request(self.get_request(self.broadcast_transaction, self.get_expected(self.broadcast_params)),
                          self._identifier)
        self.__resp = self.get_response()
        check_that(
            "'error message'",
            self.__resp["error"]["message"],
            contains_string("Day of month value is out of range 1..31: Day of month value is out of range 1..31:"
                            " unable to convert ISO-formatted string to fc::time_point_sec")
        )

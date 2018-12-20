import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_, is_integer

from common.utils import BaseTest

SUITE = {
    "description": "Test 'ECHO'"
}


@lcc.suite("Test database method")
class TestEcho(BaseTest):
    database = "database"
    get_block = "get_block"
    get_transaction = "get_transaction"

    def __init__(self):
        super().__init__()

    def setup_suite(self):
        super().setup_suite()
        self.get_identifier(self.database)

    @lcc.test("Get block")
    def test_get_block(self):
        # Get block
        lcc.set_step("Retrieve a full, signed block.")
        self.send_request(self.get_request(self.get_block), self.identifier)
        resp = self.get_response()

        # Check data in response
        lcc.set_step("Check API response")
        check_that_in(
            resp["result"],
            "previous", is_("00101555174911684721792bfe0f5eda8058ef3a")
        )

    @lcc.test("Get transaction")
    def test_get_transaction(self):
        # Get transaction
        lcc.set_step("Retrieve transaction.")
        self.send_request(self.get_request(self.get_transaction), self.identifier)
        resp = self.get_response()

        # Check data response
        lcc.set_step("Check API response")
        check_that_in(
            resp["result"],
            "ref_block_num", is_integer()
        )

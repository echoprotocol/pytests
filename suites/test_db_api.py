import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_, is_integer

from common.utils import BaseTest

SUITE = {
    "description": "Test 'Database API'"
}


@lcc.suite("Test database methods")
class TestDatabaseMethod(BaseTest):
    database_api = "database"
    get_block = "get_block"
    get_transaction = "get_transaction"

    def __init__(self):
        super().__init__()

    def setup_test(self, test):
        # Get database api identifier
        self.get_identifier(self.database_api)

    @lcc.test("Get block")
    def test_get_block(self):
        # Get block
        lcc.set_step("Retrieve a full, signed block.")
        self.send_request(self.get_request(self.get_block), self.identifier)
        resp = self.get_response()

        # Check data in response
        lcc.set_step("Check hash code of previous block")
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

        # Check number of block where this transaction is located
        lcc.set_step("Check number of block")
        check_that_in(
            resp["result"],
            "ref_block_num", is_integer()
        )

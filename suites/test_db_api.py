import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_, is_integer, check_that

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

        # Check hash code of the previous block
        lcc.set_step("Check hash code of the previous block")
        check_that(
            "'hash code of previous block'",
            resp["result"]["previous"],
            is_("00101555174911684721792bfe0f5eda8058ef3a")
        )

    @lcc.test("Get transaction")
    def test_get_transaction(self):
        # Get transaction
        lcc.set_step("Retrieve transaction.")
        self.send_request(self.get_request(self.get_transaction), self.identifier)
        resp = self.get_response()

        # Check number of the block where this transaction is located
        lcc.set_step("Check number of the block")
        check_that(
            "'number of the block'",
            resp["result"]["ref_block_num"],
            is_integer(is_(5460))
        )

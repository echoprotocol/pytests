import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_, is_integer

from common.utils import BaseTest

SUITE = {
    "description": "Test 'ECHO'"
}


@lcc.suite("Test database method")
class TestEcho(BaseTest):
    def __init__(self):
        super().__init__()
        self.database_api = "DATABASE"
        self.db_data = "database_methods.json"
        self.get_block = "GET_BLOCK"
        self.get_transaction = "GET_TRANSACTIONS"

    def get_db_identifier(self):
        lcc.set_step("Get database identifier")
        self.send_request(self.get_data(self.echo_api, self.database_api))
        resp = self.get_response()
        self.check_and_get_identifier(resp)

    @lcc.test("Get block")
    def test_get_block(self):
        # Login
        self.login_echo()

        # Get identifier
        self.get_db_identifier()

        # Get block
        lcc.set_step("Retrieve a full, signed block.")
        self.send_request(self.get_data(self.db_data, self.get_block), self.identifier)
        resp = self.get_response()

        # Check data in response
        lcc.set_step("Check API response")
        self.check_resp_format(resp)
        check_that_in(
            resp["result"],
            "previous", is_("00101555174911684721792bfe0f5eda8058ef3a")
        )

    @lcc.test("Get transaction")
    def test_get_transaction(self):
        # Login
        self.login_echo()

        # Get identifier
        self.get_db_identifier()

        # Get transaction
        lcc.set_step("Retrieve transaction.")
        self.send_request(self.get_data(self.db_data, self.get_transaction), self.identifier)
        resp = self.get_response()

        # Check data response
        lcc.set_step("Check API response")
        self.check_resp_format(resp)
        check_that_in(
            resp["result"],
            "ref_block_num", is_integer()
        )

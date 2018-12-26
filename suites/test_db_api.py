import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_, check_that

from common.utils import BaseTest

SUITE = {
    "description": "Test 'Database API'"
}


@lcc.suite("Test database methods")
class TestDatabaseMethod(BaseTest):
    __get_block = "get_block"
    __get_block_header = "get_block_header"
    __get_block_header_info = "get_block_header_info"
    __get_block_info = "block_info"
    __get_transaction = "get_transaction"
    __get_transaction_info = "transaction_info"

    def __init__(self):
        super().__init__()
        self.__resp = None

    def setup_test(self, test):
        # Get database api identifier
        self.get_identifier(self._database_api)

    @lcc.test("Get block")
    def test_get_block(self):
        # Get block
        lcc.set_step("Retrieve a full, signed block.")
        self.send_request(self.get_request(self.__get_block), self._identifier)
        self.__resp = self.get_response()

        # Check all block info
        lcc.set_step("Check block info")
        check_that(
            "'block info'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_block_info)),
        )

    @lcc.test("Get block header")
    def test_get_block_header(self):
        # Get block header
        lcc.set_step("Retrieve header of signed block.")
        self.send_request(self.get_request(self.__get_block_header), self._identifier)
        self.__resp = self.get_response()

        # Check all block header info
        lcc.set_step("Check block header info")
        check_that(
            "'block header info'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_block_header_info)),
        )

    @lcc.test("Get transaction")
    def test_get_transaction(self):
        # Get transaction
        lcc.set_step("Retrieve transaction.")
        self.send_request(self.get_request(self.__get_transaction), self._identifier)
        self.__resp = self.get_response()

        # Check all transaction info
        lcc.set_step("Check transaction info")
        check_that(
            "'transaction info'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_transaction_info)),
        )

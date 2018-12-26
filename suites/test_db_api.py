import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_, check_that, check_that_in, is_str

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
    __get_chain_properties = "get_chain_properties"
    __get_chain_properties_info = "get_chain_properties_info"
    __get_global_properties = "get_global_properties"
    __get_global_properties_info = "get_global_properties_info"
    __get_config = "get_config"
    __get_config_info = "get_config_info"
    __get_chain_id = "get_chain_id"
    __get_chain_id_info = "get_chain_id_info"
    __get_dynamic_global_properties = "get_dynamic_global_properties"
    __get_dynamic_global_properties_info = "get_dynamic_global_properties_info"

    def __init__(self):
        super().__init__()
        self.__resp = None

    def setup_test(self, test):
        # Get database api identifier
        self.get_identifier(self._database_api)

    @lcc.test("Get block")
    def test_get_block(self):
        # Get block
        lcc.set_step("Retrieve a full, signed block")
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
        lcc.set_step("Retrieve transaction")
        self.send_request(self.get_request(self.__get_transaction), self._identifier)
        self.__resp = self.get_response()

        # Check all transaction info
        lcc.set_step("Check transaction info")
        check_that(
            "'transaction info'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_transaction_info)),
        )

    @lcc.test("Get chain properties")
    def test_get_chain_properties(self):
        # Get chain properties
        lcc.set_step("Get chain properties")
        self.send_request(self.get_request(self.__get_chain_properties), self._identifier)
        self.__resp = self.get_response()

        # Check chain properties info
        lcc.set_step("Check chain properties info")
        check_that(
            "'chain properties'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_chain_properties_info)),
        )

    @lcc.test("Get global properties")
    def test_get_global_properties(self):
        # Get global properties
        lcc.set_step("Get global properties")
        self.send_request(self.get_request(self.__get_global_properties), self._identifier)
        self.__resp = self.get_response()

        # Check global properties info
        lcc.set_step("Check global properties info")
        check_that(
            "'global properties'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_global_properties_info)),
        )

    @lcc.test("Get config")
    def test_get_config(self):
        # Get config
        lcc.set_step("Get config")
        self.send_request(self.get_request(self.__get_config), self._identifier)
        self.__resp = self.get_response()

        # Check config info
        lcc.set_step("Check config info")
        check_that(
            "'config'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_config_info)),
        )

    @lcc.test("Get chain id")
    def test_get_chain_id(self):
        # Get chain id
        lcc.set_step("Get chain id")
        self.send_request(self.get_request(self.__get_chain_id), self._identifier)
        self.__resp = self.get_response()

        # Check chain id info
        lcc.set_step("Check chain id info")
        check_that(
            "'chain id'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_chain_id_info)),
        )

    @lcc.test("Get dynamic global properties")
    def test_get_dynamic_global_properties(self):
        # Get dynamic global properties
        lcc.set_step("Get dynamic global properties")
        self.send_request(self.get_request(self.__get_dynamic_global_properties), self._identifier)
        self.__resp = self.get_response()

        # Check dynamic global properties info
        lcc.set_step("Check dynamic global properties info")
        check_that_in(
            self.__resp["result"],
            "id", is_str(is_("2.1.0")),
        )

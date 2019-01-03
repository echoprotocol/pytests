import lemoncheesecake.api as lcc

from common.utils import BaseTest

SUITE = {
    "description": "Test 'History API'"
}


@lcc.suite("Test asset methods")
class TestAssetMethod(BaseTest):

    def __init__(self):
        super().__init__()
        self.__resp = None
        self.__identifier = self.get_identifier(self._history_api)

    @lcc.test("Get account history")
    @lcc.hidden()
    def test_get_account_history(self, account, stop, limit, start):  # limit=100
        pass

    @lcc.test("Get relative account history")
    @lcc.hidden()
    def test_get_relative_account_history(self, account, stop=0, limit=100, start=0):
        pass

    @lcc.test("Get account history operations")
    @lcc.hidden()
    def test_get_account_history_operations(self, account, operation_id, start, stop, limit=100):
        pass

    @lcc.test("Get contract history")
    @lcc.hidden()
    def test_get_contract_history(self, account, stop, limit, start):
        pass

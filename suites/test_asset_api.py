import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_, is_integer, is_str, has_entry, check_that

from common.utils import BaseTest

SUITE = {
    "description": "Test 'Asset API'"
}


@lcc.suite("Test asset methods")
class TestAssetMethod(BaseTest):
    asset_api = "asset"
    get_all_asset_holders = "get_all_asset_holders"
    get_all_asset_holders_count = "get_asset_holders_count"
    get_asset_holders = "get_asset_holders"
    get_name_holders = "holders"

    def __init__(self):
        super().__init__()
        self.resp_all_asset_holders = None

    def get_holders(self):
        # Get all asset holders
        lcc.set_step("Get all asset holders")
        self.send_request(self.get_request(self.get_all_asset_holders), self.identifier)
        self.resp_all_asset_holders = self.get_response()

    def setup_test(self, test):
        # Get asset api identifier
        self.get_identifier(self.asset_api)

    @lcc.test("Get all asset holders")
    def test_get_all_asset_holders(self):
        # Get all asset holders
        lcc.set_step("Get all asset holders")
        self.get_holders()

        # Check the validity of the response from the server
        lcc.set_step("Check API response")
        check_that_in(
            self.resp_all_asset_holders["result"][0],
            "asset_id", is_str(),
            "asset_id", is_("1.3.0"),
            "count", is_integer(),
            "count", is_(8)
        )

    @lcc.test("Get all asset holders count")
    def test_get_asset_holders_count(self):
        # Get all asset holders
        lcc.set_step("Get all asset holders")
        self.get_holders()

        # Get params for the test
        lcc.set_step("Get asset_id and count of holders")
        param = [self.resp_all_asset_holders["result"][0]["asset_id"]]
        holders_count = self.resp_all_asset_holders["result"][0]["count"]
        lcc.log_info("Asset id = {}, holders count = {}".format(param, holders_count))

        # Check count of holders
        lcc.set_step("Check count of holders")
        self.send_request(self.get_request(self.get_all_asset_holders_count, param), self.identifier)
        resp = self.get_response()
        check_that("'count of holders'", resp["result"], is_(holders_count))

    @lcc.test("Get asset holders")
    def test_get_asset_holders(self):
        # Get all asset holders
        lcc.set_step("Get all asset holders")
        self.get_holders()

        # Check the validity of the response from the server
        lcc.set_step("Get asset_id and count of holders")
        params = [self.resp_all_asset_holders["result"][0]["asset_id"], 0, 100]
        holders_count = self.resp_all_asset_holders["result"][0]["count"]
        lcc.log_info("Params = {}, holders count = {}".format(params, holders_count))

        # Get list of info about all holders
        lcc.set_step("Get list of holders")
        self.send_request(self.get_request(self.get_asset_holders, params), self.identifier)
        resp = self.get_response()

        # Check names of holders in list of expected holders
        lcc.set_step("Check names of holders in list of expected holders")
        for i in range(holders_count):
            check_that(
                "'list of holders'",
                resp["result"][i],
                has_entry("name", (self.get_expected(self.get_name_holders))[i])
            )

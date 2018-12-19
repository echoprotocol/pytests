import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_, is_integer, is_str

from common.utils import BaseTest

SUITE = {
    "description": "Test 'Asset API'"
}


@lcc.suite("Test login method")
class TestAssetMethod(BaseTest):
    asset_api = "asset"
    get_all_asset_holders = "get_all_asset_holders"
    get_all_asset_holders_count = "get_asset_holders_count"
    get_asset_holders = "get_asset_holders"
    get_name_holders = "holders"

    def __init__(self):
        super().__init__()

    def get_identifier_localy(self):
        lcc.set_step("Get asset identifier")
        self.send_request(self.get_request(self.asset_api))
        resp = self.get_response()
        self.get_identifier(resp)

    def setup_test(self, test_get_all_asset_holders):
        self.get_identifier_localy()

    @lcc.test("Get all asset holders")
    def test_get_all_asset_holders(self):
        # Authorization status check and request data from the database
        # self.get_identifier_localy()

        # Get all asset holders
        lcc.set_step("Requesting Access to an API")
        self.send_request(self.get_request(self.get_all_asset_holders), self.identifier)
        resp = self.get_response()

        # Check the validity of the response from the server
        lcc.set_step("Check API response")
        check_that_in(
            resp["result"][0],
            "asset_id", is_str(),
            "asset_id", is_("1.3.0"),
            "count", is_integer(),
            "count", is_(8)
        )

    @lcc.test("Get all asset holders count")
    def test_get_asset_holders_count(self):
        # # Authorization status check and request data from the database
        # self.get_asset_identifier()

        # Get all asset holders
        lcc.set_step("Requesting Access to an API")
        self.send_request(self.get_request(self.get_all_asset_holders), self.identifier)
        resp = self.get_response()

        # Check the validity of the response from the server
        lcc.set_step("Get asset_id")
        asset_id = [resp["result"][0]["asset_id"]]
        holders_count = resp["result"][0]["count"]

        # Check count of holders
        lcc.set_step("Get asset holders count")
        self.send_request(self.get_request(self.get_all_asset_holders_count, asset_id), self.identifier)
        resp = self.get_response()
        check_that_in(
            resp,
            "result", is_(holders_count)
        )

    @lcc.test("Get asset holders")
    def test_get_asset_holders(self):
        # # Authorization status check and request data from the database
        # self.get_asset_identifier()

        # Get all asset holders
        lcc.set_step("Requesting Access to an API")
        self.send_request(self.get_request(self.get_all_asset_holders), self.identifier)
        resp = self.get_response()

        # Check the validity of the response from the server
        lcc.set_step("Get asset_id and count of holders")
        params = [resp["result"][0]["asset_id"], 0, 100]
        holders_count = resp["result"][0]["count"]
        self.send_request(self.get_request(self.get_asset_holders, params), self.identifier)
        resp = self.get_response()

        # Check names of holders in list of holders
        lcc.set_step("Check names of holders in list of holders")
        for i in range(holders_count):
            check_that_in(
                resp["result"][i],
                "name", is_((self.get_expected(self.get_name_holders))[i])  # self.get_test_data,
            )

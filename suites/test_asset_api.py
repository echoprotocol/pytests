import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, is_, is_integer, is_str

from common.utils import BaseTest

SUITE = {
    "description": "Test 'Asset API'"
}


@lcc.suite("Test login method")
class TestAssetMethod(BaseTest):
    def __init__(self):
        super().__init__()
        self.asset_api = "ASSET"
        self.asset_data = "asset_methods.json"
        self.get_all_asset_holders = "GET_ALL_ASSET_HOLDERS"
        self.get_all_asset_holders_count = "GET_ASSET_HOLDERS_COUNT"
        self.get_asset_holders = "GET_ASSET_HOLDERS"
        self.get_test_data = "test_data.json"
        self.get_name_holders = "HOLDERS"

    def get_asset_identifier(self):
        lcc.set_step("Get asset identifier")
        self.send_request(self.get_data(self.echo_api, self.asset_api))
        resp = self.get_response()
        self.check_and_get_identifier(resp)

    @lcc.test("Get all asset holders")
    def test_get_all_asset_holders(self):
        # Login
        self.login_echo()

        # Authorization status check and request data from the database
        self.get_asset_identifier()

        # Get all asset holders
        lcc.set_step("Requesting Access to an API")
        self.send_request(self.get_data(self.asset_data, self.get_all_asset_holders), self.identifier)
        resp = self.get_response()

        # Check the validity of the response from the server
        lcc.set_step("Check API response")
        self.check_resp_format(resp)
        check_that_in(
            resp["result"][0],
            "asset_id", is_str(),
            "asset_id", is_("1.3.0"),
            "count", is_integer(),
            "count", is_(8)
        )

    @lcc.test("Get all asset holders count")
    def test_get_asset_holders_count(self):
        # Login
        self.login_echo()

        # Authorization status check and request data from the database
        self.get_asset_identifier()

        # Get all asset holders
        lcc.set_step("Requesting Access to an API")
        self.send_request(self.get_data(self.asset_data, self.get_all_asset_holders), self.identifier)
        resp = self.get_response()

        # Check the validity of the response from the server
        lcc.set_step("Get asset_id")
        asset_id = [resp["result"][0]["asset_id"]]
        holders_count = resp["result"][0]["count"]

        # Check count of holders
        lcc.set_step("Get asset holders count")
        self.send_request(self.get_data(self.asset_data, self.get_all_asset_holders_count, asset_id), self.identifier)
        resp = self.get_response()
        self.check_resp_format(resp)
        check_that_in(
            resp,
            "result", is_(holders_count)
        )

    @lcc.test("Get asset holders")
    def test_get_asset_holders(self):
        # Login
        self.login_echo()

        # Authorization status check and request data from the database
        self.get_asset_identifier()

        # Get all asset holders
        lcc.set_step("Requesting Access to an API")
        self.send_request(self.get_data(self.asset_data, self.get_all_asset_holders), self.identifier)
        resp = self.get_response()

        # Check the validity of the response from the server
        lcc.set_step("Get asset_id and count of holders")
        params = [resp["result"][0]["asset_id"], 0, 100]
        holders_count = resp["result"][0]["count"]
        self.send_request(self.get_data(self.asset_data, self.get_asset_holders, params),
                          self.identifier)
        resp = self.get_response()
        self.check_resp_format(resp)

        # Check names of holders in list of holders
        lcc.set_step("Check names of holders in list of holders")
        for i in range(holders_count):
            check_that_in(
                resp["result"][i],
                "name", is_((self.get_data(self.get_test_data, self.get_name_holders))[i])
            )

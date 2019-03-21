# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_integer, has_entry, check_that, is_

from common.base_test import BaseTest

SUITE = {
    "description": "Check all the methods belonging to the asset_api"
}


@lcc.suite("Testing 'Asset API' methods call")
@lcc.hidden()
class AssetApi(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = self.get_identifier("asset")
        self.resp_all_asset_holders = None

    def get_holders(self):
        lcc.set_step("Get all asset holders")
        response_id = self.send_request(self.get_request("get_all_asset_holders"), self.__api_identifier)
        self.resp_all_asset_holders = self.get_response(response_id)

    @lcc.test("Get all asset holders")
    def test_get_all_asset_holders(self):
        lcc.set_step("Get all asset holders")
        self.get_holders()

        lcc.set_step("Check asset_id and count of all asset holders")
        check_that(
            "'contract result'",
            self.resp_all_asset_holders["result"],
            is_(self.get_expected("get_all_asset_holders")),
        )

    @lcc.test("Get all asset holders count")
    def test_get_asset_holders_count(self):
        lcc.set_step("Get all asset holders")
        self.get_holders()

        for asset in range(len(self.resp_all_asset_holders["result"])):
            lcc.set_step("Get asset_id and count of holders")
            param = [self.resp_all_asset_holders["result"][asset]["asset_id"]]
            holders_count = self.resp_all_asset_holders["result"][asset]["count"]
            lcc.log_info("Asset id = {}, holders count = {}".format(param, holders_count))

            lcc.set_step("Check count of holders")
            response_id = self.send_request(self.get_request("get_asset_holders_count", param),
                                            self.__api_identifier)
            response = self.get_response(response_id)
            check_that("'count of holders'", response["result"], is_integer(holders_count))

    @lcc.test("Get asset holders")
    def test_get_asset_holders(self):
        lcc.set_step("Get all asset holders")
        self.get_holders()

        lcc.set_step("Get asset_id and count of holders")
        params = [self.resp_all_asset_holders["result"][0]["asset_id"], 0, 100]
        holders_count = self.resp_all_asset_holders["result"][0]["count"]
        lcc.log_info("Params = {}, holders count = {}".format(params, holders_count))

        lcc.set_step("Get list of holders")
        response_id = self.send_request(self.get_request("get_asset_holders", params), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check names of holders in list of expected holders")
        for i in range(holders_count):
            expected_keys = ["name", "account_id", "amount"]
            for j in range(len(expected_keys)):
                check_that(
                    "'holder №{}'".format(i + 1),
                    response["result"][i],
                    has_entry(
                        expected_keys[j], ((self.get_expected("get_holders"))[i])[j],
                    ),
                )

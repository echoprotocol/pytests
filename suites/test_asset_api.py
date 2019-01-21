# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_integer, has_entry, check_that, is_

from common.base_test import BaseTest

SUITE = {
    "description": "Test 'Asset API'"
}


@lcc.suite("Test asset methods")
class TestAssetMethod(BaseTest):
    __get_all_asset_holders = "get_all_asset_holders"
    __get_all_asset_holders_count = "get_asset_holders_count"
    __get_asset_holders = "get_asset_holders"
    __get_holders = "get_holders"

    def __init__(self):
        super().__init__()
        self.__resp = None
        self.__identifier = self.get_identifier(self._asset_api)
        self.resp_all_asset_holders = None

    def get_holders(self):
        lcc.set_step("Get all asset holders")
        self.send_request(self.get_request(self.__get_all_asset_holders), self.__identifier)
        self.resp_all_asset_holders = self.get_response()

    @lcc.test("Get all asset holders")
    def test_get_all_asset_holders(self):
        lcc.set_step("Get all asset holders")
        self.get_holders()

        lcc.set_step("Check asset_id and count of all asset holders")
        # check_that_in(
        #     self.resp_all_asset_holders["result"],
        #     "asset_id", is_str("1.3.0"),
        #     "count", is_integer(16)
        # )
        check_that(
            "'contract result'",
            self.resp_all_asset_holders["result"],
            is_(self.get_expected(self.__get_all_asset_holders)),
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
            self.send_request(self.get_request(self.__get_all_asset_holders_count, param), self.__identifier)
            self.__resp = self.get_response()
            check_that("'count of holders'", self.__resp["result"], is_integer(holders_count))

    @lcc.test("Get asset holders")
    def test_get_asset_holders(self):
        lcc.set_step("Get all asset holders")
        self.get_holders()

        lcc.set_step("Get asset_id and count of holders")
        params = [self.resp_all_asset_holders["result"][0]["asset_id"], 0, 100]
        holders_count = self.resp_all_asset_holders["result"][0]["count"]
        lcc.log_info("Params = {}, holders count = {}".format(params, holders_count))

        lcc.set_step("Get list of holders")
        self.send_request(self.get_request(self.__get_asset_holders, params), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check names of holders in list of expected holders")
        for i in range(holders_count):
            expected_keys = ["name", "account_id", "amount"]
            for j in range(len(expected_keys)):
                check_that(
                    "'holder №{}'".format(i + 1),
                    self.__resp["result"][i],
                    has_entry(
                        expected_keys[j], ((self.get_expected(self.__get_holders))[i])[j],
                    ),
                )

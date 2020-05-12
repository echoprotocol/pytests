# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, require_that, has_length, equal_to, is_none, is_list

from common.base_test import BaseTest
from project import MIN_ETH_WITHDRAW, GAS_PRICE, MIN_ETH_WITHDRAW_FEE


SUITE = {
    "description": "Methods: 'get_eth_sidechain_fees'"
}


@lcc.prop("main", "type")
@lcc.tags(
    "api", "database_api", "sidechain", "sidechain_ethereum",
    "database_api_sidechain_ethereum", "get_eth_sidechain_fees",
    "database_api_objects"
)
@lcc.suite("Check work of methods: 'get_eth_sidechain_fees'", rank=1)
class GetEthSidechainFees(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of methods: 'get_eth_sidechain_fees'")
    def method_main_check(self):
        lcc.set_step("Check Ethereum sidechain min withdrawal and min withdrawal fee in method 'get_eth_sidechain_fees'")
        response_id = self.send_request(self.get_request("get_eth_sidechain_fees"),
                                        self.__database_api_identifier)
        get_eth_sidechain_fees_result = self.get_response(response_id)["result"]
        if require_that("result", get_eth_sidechain_fees_result, is_list()):
            check_that("eth_withdrawal_min", int(get_eth_sidechain_fees_result[0]), equal_to(MIN_ETH_WITHDRAW*GAS_PRICE))
            check_that("min_eth_withdrawal_fee", int(get_eth_sidechain_fees_result[1]), equal_to(MIN_ETH_WITHDRAW_FEE * GAS_PRICE))

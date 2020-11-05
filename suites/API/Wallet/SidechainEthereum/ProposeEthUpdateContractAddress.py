# -*- coding: utf-8 -*-
import time
from project import ETHEREUM_URL
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
import requests
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import (
    check_that, equal_to, not_equal_to
)
# from lemoncheesecake.matching import check_that, equal_to, not_equal_to, require_that

SUITE = {
    "description": "Method 'propose_eth_update_contract_address'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_sidechain_ethereum", "wallet_propose_eth_update_contract_address")
@lcc.suite("Check work of method 'propose_eth_update_contract_address'", rank=1)
class ProposeEthUpdateContractAddress(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.init0 = None
        self.init1 = None
        self.init2 = None
        self.init3 = None
        self.init4 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        lcc.set_step("Get initial account ids")
        self.init0 = self.get_account_id('init0', self.__database_api_identifier, self.__registration_api_identifier)
        self.init1 = self.get_account_id('init1', self.__database_api_identifier, self.__registration_api_identifier)
        self.init2 = self.get_account_id('init2', self.__database_api_identifier, self.__registration_api_identifier)
        self.init3 = self.get_account_id('init3', self.__database_api_identifier, self.__registration_api_identifier)
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        lcc.log_info(
            "Initial account ids: '{}', '{}', '{}', '{}', '{}', '{}'".format(
                self.init0, self.init1, self.init2, self.init3, self.init4, self.init5
            )
        )

    def rpc_call(self, method, params):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        return payload

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.disabled()
    @lcc.test("Simple work of method 'wallet_propose_eth_update_contract_address'")
    def method_main_check(self, get_random_eth_address):
        self.unlock_wallet()
        self.import_key('init0', 'init1', 'init2', 'init3', 'init4', 'init5')
        payload = self.rpc_call(
            "eth_call", [{
                "to": "0xF663f3e27B5c5beaf7A0b4A7355BF69DfC5671E8",
                "data": "0x5c60da1b"
            }, "latest"]
        )
        response = requests.post(ETHEREUM_URL, json=payload).json()
        address_of_current_implementation = response['result']

        new_eth_contract_address = get_random_eth_address

        lcc.set_step("Transfer assets to fee payer account")
        self.send_wallet_request(
            "transfer", [self.init5, '1.2.1', 10, self.echo_asset, True], log_response=False
        )
        self.produce_block(self.__database_api_identifier)
        lcc.log_info("Assets transfered")

        proposal = self.send_wallet_request(
            "propose_eth_update_contract_address",
            [self.init0, self.get_expiration_time(30), new_eth_contract_address],
            log_response=True
        )

        lcc.log_info("Search for a block with proposal_id")
        block = int(proposal['result']['ref_block_num'])
        proposal_id = self.get_proposal_id_from_next_blocks(block)
        lcc.log_info("Block found, proposal id in block: '{}'".format(proposal_id))

        proposal_params = {
            "active_approvals_to_add": [],
            "active_approvals_to_remove": [],
            "key_approvals_to_add": [],
            "key_approvals_to_remove": []
        }
        proposal_params['active_approvals_to_add'].extend([self.init0, self.init1, self.init2, self.init3, self.init4])
        self.send_wallet_request(
            "approve_proposal", [self.init0, proposal_id, proposal_params, True], log_response=False
        )

        lcc.set_step(
            "Waiting for maintenance and release of few blocks and check that new eth contract address implemented"
        )

        self.produce_block(self.__database_api_identifier)
        time.sleep(40)
        self.produce_block(self.__database_api_identifier)
        payload = self.rpc_call(
            "eth_call", [{
                "to": "0xF663f3e27B5c5beaf7A0b4A7355BF69DfC5671E8",
                "data": "0x5c60da1b"
            }, "latest"]
        )
        response = requests.post(ETHEREUM_URL, json=payload).json()
        address_of_new_implementation = response['result']
        check_that('eth contract address', address_of_new_implementation, not_equal_to(address_of_current_implementation))
        expected_address = "{}{}".format('0x000000000000000000000000', new_eth_contract_address)
        check_that('new eth contract address', address_of_new_implementation, equal_to(expected_address))

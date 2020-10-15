# -*- coding: utf-8 -*-
import time

from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.disabled()
    @lcc.test("Simple work of method 'wallet_propose_eth_update_contract_address'")
    def method_main_check(self, get_random_valid_account_name, get_random_eth_address, get_random_btc_public_key):
        self.unlock_wallet()
        self.import_key('init0', 'init1', 'init2', 'init3', 'init4', 'init5')
        lcc.log_info("{}".format(self.get_expiration_time(15)))
        proposal = self.send_wallet_request(
            "propose_eth_update_contract_address", [self.init0, self.get_expiration_time(15), "0e7057518879d5DE1F842b77e8F6F3e22931a1be"], log_response=True
        )
        lcc.log_info("Search for a block with parameter change proposal")
        block = int(proposal['result']['ref_block_num'])
        proposal_id = self.get_proposal_id_from_next_blocks(block)
        lcc.log_info("Block found, proposal id in block: '{}'".format(proposal_id))

        proposal = self.send_wallet_request(
            "get_object", [proposal_id], log_response=True
        )
        lcc.log_info("{}".format(proposal))

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
        proposal = self.send_wallet_request(
            "get_object", [proposal_id], log_response=True
        )
        lcc.log_info("{}".format('asdsad'))

        lcc.set_step(
            "Waiting for maintenance and release of two blocks and check that new committee member were activated"
        )
        time.sleep(15)
        self.produce_block(self.__database_api_identifier)
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        get_global_properties = self.get_response(response_id)["result"]
        lcc.log_info("{}".format(get_global_properties))

        # set_password
        # unlock
        # import_key "1.2.6", "1.2.7", "1.2.8", "1.2.9", "1.2.10"
        # transfer 1.2.10 1.2.1 10 ECHO true
        # propose_eth_update_contract_address 1.2.6 "2020-10-13T14:02:44" "0e7057518879d5DE1F842b77e8F6F3e22931a1be"
        # approve_proposal 1.2.6 1.5.0 {"active_approvals_to_add": ["1.2.6", "1.2.7", "1.2.8", "1.2.9", "1.2.10"],"active_approvals_to_remove": [],"key_approvals_to_add": [],"key_approvals_to_remove": []} true 

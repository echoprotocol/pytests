# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, not_equal_to
from common.base_test import BaseTest
import time

from project import INIT0_PK, INIT1_PK, INIT2_PK, INIT3_PK, INIT4_PK
SUITE = {
    "description": "Operation 'committee_member_update_global_parameters'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "committee_member_operations", "committee_member_update_global_parameters")
@lcc.suite("Check work of method 'committee_member_update_global_parameters'", rank=1)
class CommitteeMemberUpdateGlobalParameters(BaseTest):
    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.committee_members_info = None
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
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        self.committee_members_info = self.get_active_committee_members_info(self.__database_api_identifier)
        self.init0 = self.committee_members_info[0]["account_id"]
        self.init1 = self.committee_members_info[1]["account_id"]
        self.init2 = self.committee_members_info[2]["account_id"]
        self.init3 = self.committee_members_info[3]["account_id"]
        self.init4 = self.committee_members_info[4]["account_id"]
        lcc.log_info("Echo  initial accounts: {}, {}, {}, {}, {}".format(
                     self.init0, self.init1, self.init2, self.init3, self.init4))

    def produce(self):
        time.sleep(50)
        self.produce_block(self.__database_api_identifier)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of operation 'committee_member_update_global_parameters'")
    def method_main_check(self):
        lcc.set_step("Get global properties and update it")
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        global_properties = self.get_response(response_id)["result"]
        if global_properties["parameters"]["maintenance_interval"] > 50:
            lcc.log_info(
                "Test did not find required conditions: 'maintenance_interval > 50. "
                "Test of operation 'committee_member_update_global_parameters' was skipped."
            )
        else:
            _time_net_1mb = global_properties["parameters"]["echorand_config"]["_time_net_1mb"]
            _time_net_1mb += 1
            lcc.log_info("Update echorand_config parameter '_time_net_1mb', new value: {}".format(_time_net_1mb))
            lcc.set_step("Perform 'committee_member_update_global_parameters' operation")
            operation = self.echo_ops.get_committee_member_update_global_parameters_operation(
                echo=self.echo,
                _time_net_1mb=_time_net_1mb,
                signer=INIT0_PK
            )
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            lcc.log_info("Operation was collected")
            lcc.set_step("Make proposal of `committee_member_update_global_parameters`")
            operation = self.echo_ops.get_proposal_create_operation(
                echo=self.echo,
                fee_paying_account=self.init0,
                proposed_ops=collected_operation,
                expiration_time=self.get_expiration_time(30),
                review_period_seconds=10,
                signer=INIT0_PK
            )
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=operation)
            proposal_id = broadcast_result["trx"]["operation_results"][0][1]
            lcc.log_info("Proposal was created: {}".format(proposal_id))
            lcc.set_step("Make voting for new global parameters")
            operation = self.echo_ops.get_proposal_update_operation(
                echo=self.echo,
                fee_paying_account=self.init0,
                proposal=proposal_id,
                active_approvals_to_add=[self.init0, self.init1, self.init2, self.init3, self.init4],
                active_approvals_to_remove=[],
                key_approvals_to_add=[],
                key_approvals_to_remove=[],
                signer=[INIT0_PK, INIT1_PK, INIT2_PK, INIT3_PK, INIT4_PK]
            )
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
            lcc.log_info("All committee member has voted")
            lcc.set_step("Waiting for maintenance and release of block and check that parameters have been updated")
            self.produce()
            response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
            current_global_properties = self.get_response(response_id)["result"]
            check_that(
                "global",
                global_properties, not_equal_to(current_global_properties),
                quiet=True
            )

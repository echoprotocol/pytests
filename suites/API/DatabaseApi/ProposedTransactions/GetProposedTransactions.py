# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_list, is_true, require_that

SUITE = {
    "description": "Methods: 'get_proposed_transactions', 'get_objects' (proposal object)"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags(
    "api", "database_api", "database_api_proposed_transactions", "get_proposed_transactions", "database_api_objects",
    "get_objects"
)
@lcc.suite("Check work of method 'get_proposed_transactions'", rank=1)
class GetProposedTransactions(BaseTest):

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
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo accounts are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_proposed_transactions'")
    def method_main_check(self):
        lcc.set_step("Get proposed transactions for '{}' account".format(self.echo_acc0))
        response_id = self.send_request(
            self.get_request("get_proposed_transactions", [self.echo_acc0]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call 'get_proposed_transactions' with id='{}' parameter".format(self.echo_acc0))

        lcc.set_step("Check 'get_proposed_transactions' method result")
        require_that("proposed transactions", response["result"], is_list([]))


@lcc.prop("positive", "type")
@lcc.tags(
    "api", "database_api", "database_api_proposed_transactions", "get_proposed_transactions", "database_api_objects",
    "get_objects"
)
@lcc.suite("Positive testing of methods: 'get_proposed_transactions', 'get_objects' (proposal object)", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
        lcc.log_info("Registration API identifier is '{}'".format(self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        self.echo_acc1 = self.get_account_id(
            self.accounts[1], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Propose transaction using proposal_create operation and get info about it")
    @lcc.depends_on(
        "API.DatabaseApi.ProposedTransactions.GetProposedTransactions.GetProposedTransactions.method_main_check"
    )
    def get_info_about_proposed_transaction(self):
        lcc.set_step("Collect 'get_proposed_transactions' operation")
        transfer_operation = self.echo_ops.get_transfer_operation(
            echo=self.echo, from_account_id=self.echo_acc1, to_account_id=self.echo_acc0
        )
        lcc.set_step("Broadcast proposal transaction that contains simple transfer operation to the ECHO network")
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        proposal_expiration = self.get_expiration_time(60)
        proposal_create_operation = self.echo_ops.get_proposal_create_operation(
            echo=self.echo,
            fee_paying_account=self.echo_acc0,
            proposed_ops=collected_operation,
            expiration_time=proposal_expiration
        )
        collected_operation = self.collect_operations(proposal_create_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(
            echo=self.echo, list_operations=collected_operation, log_broadcast=False
        )
        require_that(
            "broadcast transaction complete successfully",
            self.is_operation_completed(broadcast_result, 1),
            is_true(),
            quiet=True
        )
        proposal_id = broadcast_result["trx"]["operation_results"][0][1]
        broadcasted_proposed_operation = broadcast_result["trx"]["operations"][0][1]["proposed_ops"][0]["op"]

        lcc.set_step("Get proposed transactions for '{}' account".format(self.echo_acc1))
        response_id = self.send_request(
            self.get_request("get_proposed_transactions", [self.echo_acc1]), self.__database_api_identifier
        )
        get_proposed_transactions_results = self.get_response(response_id)["result"]
        lcc.log_info("Call 'get_proposed_transactions' with id='{}' parameter".format(self.echo_acc1))

        lcc.set_step("Check 'get_proposed_transactions' method result")
        for proposal_object in get_proposed_transactions_results:
            if proposal_object["id"] == proposal_id:
                break

        self.object_validator.validate_proposal_object(self, proposal_object)
        check_that(
            "'proposed operation'",
            proposal_object["proposed_transaction"]["operations"][0],
            is_list(broadcasted_proposed_operation),
            quiet=True
        )
        check_that(
            "'proposal expiration'", proposal_object["expiration_time"], equal_to(proposal_expiration), quiet=True
        )
        check_that(
            "'required active approval'",
            proposal_object["required_active_approvals"],
            is_list([self.echo_acc1]),
            quiet=True
        )

        lcc.set_step("Get proposal object")
        params = [proposal_id]
        response_id = self.send_request(self.get_request("get_objects", [params]), self.__database_api_identifier)
        get_objects_results = self.get_response(response_id)["result"]
        lcc.log_info("Call 'get_objects' with params='{}'".format(params))

        lcc.set_step("Check 'get_proposed_transactions' method result")
        for get_objects_proposal in get_objects_results:
            if get_objects_proposal["id"] == proposal_id:
                break

        lcc.set_step(
            "Check the identity of returned results of api-methods: 'get_proposed_transactions', 'get_objects'"
        )
        require_that('proposal object', get_objects_proposal, equal_to(proposal_object), quiet=True)

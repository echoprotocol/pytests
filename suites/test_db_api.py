# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_, check_that, check_that_in, is_str, is_integer, equal_to, is_true, is_none, \
    is_list, is_dict

from common.base_test import BaseTest

SUITE = {
    "description": "Test 'Database API'"
}


@lcc.suite("Test database methods")
class TestDatabaseMethod(BaseTest):
    __get_objects = "get_objects"
    __set_subscribe_callback = "set_subscribe_callback"
    __set_pending_transaction_callback = "set_pending_transaction_callback"
    __set_block_applied_callback = "set_block_applied_callback"
    __cancel_all_subscriptions = "cancel_all_subscriptions"
    __get_block = "get_block"
    __get_block_header = "get_block_header"
    __get_transaction = "get_transaction"
    __get_chain_properties = "get_chain_properties"
    __get_global_properties = "get_global_properties"
    __get_config = "get_config"
    __get_chain_id = "get_chain_id"
    __get_dynamic_global_properties = "get_dynamic_global_properties"
    __get_key_references = "get_key_references"
    __get_account_by_name = "get_account_by_name"
    __get_accounts = "get_accounts"
    __get_full_accounts = "get_full_accounts"
    __get_full_accounts_ids_exp = "get_full_accounts_ids"
    __get_full_accounts_names_exp = "get_full_accounts_names"
    __get_account_references = "get_account_references"
    __lookup_account_names = "lookup_account_names"
    __lookup_accounts = "lookup_accounts"
    __get_account_count = "get_account_count"
    __get_account_balances = "get_account_balances"
    __get_account_balances_empty_exp = "get_account_balances_empty"
    __get_named_account_balances = "get_named_account_balances"
    __get_vested_balances = "get_vested_balances"
    __get_assets = "get_assets"
    __list_assets = "list_assets"
    __lookup_asset_symbols = "lookup_asset_symbols"
    __get_call_orders = "get_call_orders"
    __get_settle_orders = "get_settle_orders"
    __get_margin_positions = "get_margin_positions"
    __get_witnesses = "get_witnesses"
    __get_witness_by_account = "get_witness_by_account"
    __get_witness_count = "get_witness_count"
    __get_committee_members = "get_committee_members"
    __get_committee_member_by_account = "get_committee_member_by_account"
    __get_workers_by_account = "get_workers_by_account"
    __lookup_vote_ids = "lookup_vote_ids"
    __get_transaction_hex = "get_transaction_hex"
    __get_required_signatures = "get_required_signatures"
    __get_potential_signatures = "get_potential_signatures"
    __get_potential_address_signatures = "get_potential_address_signatures"
    __verify_authority = "verify_authority"
    __verify_account_authority = "verify_account_authority"
    __validate_transaction = "validate_transaction"
    __get_required_fees = "get_required_fees"
    __contract_operations = "contract_operations"
    __get_proposed_transactions = "get_proposed_transactions"
    __get_all_contracts = "get_all_contracts"
    __get_contract_logs = "get_contract_logs"
    __get_contract_result = "get_contract_result"
    __get_contract = "get_contract"
    __call_contract_no_changing_state = "call_contract_no_changing_state"
    __get_contracts = "get_contracts"
    __get_contract_balances = "get_contract_balances"

    def __init__(self):
        super().__init__()
        self.__resp = None
        self.__identifier = self.get_identifier(self._database_api)

    @lcc.test("Get objects")
    def test_get_objects(self):
        lcc.set_step("Get objects 'account' and 'asset'")
        self.send_request(self.get_request(self.__get_objects), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get objects 'account' and 'asset'")
        check_that(
            "'account' and 'asset'",
            self.__resp["result"],
            is_list(self.get_expected(self.__get_objects)),
        )

    @lcc.test("Set subscribe callback")
    def test_set_subscribe_callback(self):
        lcc.set_step("Set subscribe callback")
        self.send_request(self.get_request(self.__set_subscribe_callback), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check set subscribe callback")
        check_that(
            "'subscribe callback'",
            self.__resp["result"],
            is_none(),
        )

    @lcc.test("Set pending transaction callback")
    @lcc.disabled()
    def test_set_pending_transaction_callback(self):
        lcc.set_step("Set pending transaction callback")
        self.send_request(self.get_request(self.__set_pending_transaction_callback), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check set pending transaction callback")
        check_that(
            "'pending transaction callback'",
            self.__resp["result"],
            is_none(),
        )

    @lcc.test("Set block applied callback")
    @lcc.disabled()
    def test_set_block_applied_callback(self):
        lcc.set_step("Set block applied callback")
        self.send_request(self.get_request(self.__set_block_applied_callback), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check set block applied callback")
        check_that(
            "'block applied callback'",
            self.__resp["result"],
            is_none(),
        )

    @lcc.test("Cancel all subscriptions")
    def test_cancel_all_subscriptions(self):
        lcc.set_step("Cancel all subscriptions")
        self.send_request(self.get_request(self.__cancel_all_subscriptions), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Cancel all subscriptions")
        check_that(
            "'cancel all subscriptions'",
            self.__resp["result"],
            is_none(),
        )

    @lcc.test("Get block")
    def test_get_block(self):
        lcc.set_step("Retrieve a full, signed block")
        self.send_request(self.get_request(self.__get_block), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check block info")
        check_that(
            "'block info'",
            self.__resp["result"],
            is_dict(self.get_expected(self.__get_block)),
        )

    @lcc.test("Get block header")
    def test_get_block_header(self):
        lcc.set_step("Retrieve header of signed block")
        self.send_request(self.get_request(self.__get_block_header), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check block header info")
        check_that(
            "'block header info'",
            self.__resp["result"],
            is_dict(self.get_expected(self.__get_block_header)),
        )

    @lcc.test("Get transaction")
    def test_get_transaction(self):
        lcc.set_step("Retrieve transaction")
        self.send_request(self.get_request(self.__get_transaction), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check transaction info")
        check_that(
            "'transaction info'",
            self.__resp["result"],
            is_dict(self.get_expected(self.__get_transaction)),
        )

    @lcc.test("Get recent transaction by id")
    @lcc.hidden()
    def test_get_recent_transaction_by_id(self, trans_id):
        pass

    @lcc.test("Get chain properties")
    def test_get_chain_properties(self):
        lcc.set_step("Get chain properties")
        self.send_request(self.get_request(self.__get_chain_properties), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check chain properties info")
        check_that(
            "'chain properties'",
            self.__resp["result"],
            is_dict(self.get_expected(self.__get_chain_properties)),
        )

    @lcc.test("Get global properties")
    def test_get_global_properties(self):
        lcc.set_step("Get global properties")
        self.send_request(self.get_request(self.__get_global_properties), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check global properties info")
        check_that(
            "'global properties'",
            self.__resp["result"],
            is_dict(self.get_expected(self.__get_global_properties)),
        )

    @lcc.test("Get config")
    def test_get_config(self):
        lcc.set_step("Get config")
        self.send_request(self.get_request(self.__get_config), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check config info")
        check_that(
            "'config'",
            self.__resp["result"],
            is_dict(self.get_expected(self.__get_config)),
        )

    @lcc.test("Get chain id")
    def test_get_chain_id(self):
        lcc.set_step("Get chain id")
        self.send_request(self.get_request(self.__get_chain_id), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check chain id info")
        check_that(
            "'chain id'",
            self.__resp["result"],
            is_str(self.get_expected(self.__get_chain_id)),
        )

    @lcc.test("Get dynamic global properties")
    def test_get_dynamic_global_properties(self):
        lcc.set_step("Get dynamic global properties")
        self.send_request(self.get_request(self.__get_dynamic_global_properties), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check dynamic global properties info")
        check_that_in(
            self.__resp["result"],
            "id", is_str("2.1.0"),
        )

    @lcc.test("Get key references")
    def test_get_key_references(self):
        lcc.set_step("Get key references")
        self.send_request(self.get_request(self.__get_key_references), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check key references")
        check_that(
            "'key references'",
            self.__resp["result"],
            is_list(self.get_expected(self.__get_key_references)),
        )

    @lcc.test("Get accounts")
    def test_get_accounts(self):
        lcc.set_step("Get accounts")
        self.send_request(self.get_request(self.__get_accounts), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check accounts")
        check_that(
            "'accounts'",
            self.__resp["result"],
            is_list(self.get_expected(self.__get_accounts)),
        )

    @lcc.test("Get full accounts by ids")
    def test_get_full_accounts_ids(self):
        lcc.set_step("Get full accounts by ids")
        params = [["1.2.6", "1.2.7", "1.2.8", "1.2.9", "1.2.10", "1.2.11", "1.2.14"], False]
        self.send_request(self.get_request(self.__get_full_accounts, params), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check full accounts by ids")
        check_that(
            "'full accounts by ids'",
            self.__resp["result"],
            is_list(self.get_expected(self.__get_full_accounts_ids_exp)),
        )

    @lcc.test("Get full accounts by names")
    def test_get_full_accounts_names(self):
        lcc.set_step("Get full accounts by names")
        params = [["init0", "init1", "init2", "init3", "init4", "init5", "nathan", "test124"], False]
        self.send_request(self.get_request(self.__get_full_accounts, params), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check full accounts by names")
        check_that(
            "'full accounts by names'",
            self.__resp["result"],
            is_list(self.get_expected(self.__get_full_accounts_names_exp)),
        )

    @lcc.test("Get account by name")
    def test_get_account_by_name(self):
        lcc.set_step("Get account by name")
        self.send_request(self.get_request(self.__get_account_by_name), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check account by name")
        check_that(
            "'init2'",
            self.__resp["result"],
            is_dict(self.get_expected(self.__get_account_by_name)),
        )

    @lcc.test("Get account references")
    @lcc.tags("don't work")
    def test_get_account_references(self):
        lcc.set_step("Get account references")
        # todo нет необходимого аккаунта для проверки
        self.send_request(self.get_request(self.__get_account_references), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check account references")
        check_that(
            "'1.2.28'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_account_references)),
        )

    @lcc.test("Lookup account names")
    def test_lookup_account_names(self):
        lcc.set_step("Lookup account names")
        self.send_request(self.get_request(self.__lookup_account_names), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check lookup account names")
        check_that(
            "'lookup account names'",
            self.__resp["result"],
            is_list(self.get_expected(self.__lookup_account_names)),
        )

    @lcc.test("Lookup accounts")
    def test_lookup_accounts(self):
        lcc.set_step("Lookup accounts")
        # todo непонятно как работает limit
        self.send_request(self.get_request(self.__lookup_accounts), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check lookup accounts")
        check_that(
            "'lookup accounts'",
            self.__resp["result"],
            is_list(self.get_expected(self.__lookup_accounts)),
        )

    @lcc.test("Get account count")
    def test_get_account_count(self):
        lcc.set_step("Get account count")
        self.send_request(self.get_request(self.__get_account_count), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get account count")
        check_that(
            "'account count'",
            self.__resp["result"],
            is_integer(29)
        )

    @lcc.test("Get account balances, empty param: assets")
    def test_get_account_balances_empty_assets(self):
        lcc.set_step("Get account balances")
        params = ["1.2.8", []]
        self.send_request(self.get_request(self.__get_account_balances, params), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get account balances")
        check_that(
            "'account balances'",
            self.__resp["result"],
            is_list(self.get_expected(self.__get_account_balances_empty_exp)),
        )

    @lcc.test("Get account balances")
    def test_get_account_balances(self):
        lcc.set_step("Get account balances")
        params = ["1.2.8", ["1.3.0", "1.3.1", "1.3.2"]]
        self.send_request(self.get_request(self.__get_account_balances, params), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get account balances")
        check_that(
            "'account balances'",
            self.__resp["result"],
            is_list(self.get_expected(self.__get_account_balances)),
        )

    @lcc.test("Get named account balances, empty param: assets")
    def test_get_named_account_balances_empty_assets(self):
        lcc.set_step("Get named account balances")
        params = ["init2", []]
        self.send_request(self.get_request(self.__get_named_account_balances, params), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get named account balances")
        check_that(
            "'named account balances'",
            self.__resp["result"],
            is_list(self.get_expected(self.__get_account_balances_empty_exp)),
        )

    @lcc.test("Get named account balances")
    def test_get_named_account_balances(self):
        lcc.set_step("Get named account balances")
        params = ["init2", ["1.3.0", "1.3.1", "1.3.2"]]
        self.send_request(self.get_request(self.__get_named_account_balances, params), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get named account balances")
        check_that(
            "'named account balances'",
            self.__resp["result"],
            is_list(self.get_expected(self.__get_account_balances)),
        )

    @lcc.test("Get balance objects")
    @lcc.hidden()
    def test_get_balance_objects(self, addrs):
        pass

    @lcc.test("Get vested balances")
    @lcc.tags("don't work")
    @lcc.disabled()
    def test_get_vested_balances(self):
        # todo нет нужных balance_ids
        lcc.set_step("Get vested balances")
        self.send_request(self.get_request(self.__get_vested_balances), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get vested balances")
        check_that(
            "'vested balances'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_account_balances)),
        )

    @lcc.test("Get vesting balances")
    @lcc.hidden()
    def test_get_vesting_balances(self, account_id):
        pass

    @lcc.test("Get assets")
    def test_get_assets(self):
        lcc.set_step("Get assets")
        self.send_request(self.get_request(self.__get_assets), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get assets")
        check_that(
            "'assets'",
            self.__resp["result"],
            is_list(self.get_expected(self.__get_assets)),
        )

    @lcc.test("List assets")
    def test_list_assets(self):
        lcc.set_step("List assets")
        # todo чувствителен к регистру
        self.send_request(self.get_request(self.__list_assets), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check list assets")
        check_that(
            "'list assets'",
            self.__resp["result"],
            is_list(self.get_expected(self.__list_assets)),
        )

    @lcc.test("Lookup asset symbols")
    def test_lookup_asset_symbols(self):
        lcc.set_step("Lookup asset symbols")
        params = [["ECHO", "ECHOTEST"]]
        self.send_request(self.get_request(self.__lookup_asset_symbols, params), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check lookup asset symbols")
        check_that(
            "'lookup asset symbols'",
            self.__resp["result"],
            is_list(self.get_expected(self.__lookup_asset_symbols)),
        )

    @lcc.test("Lookup asset ids")
    def test_lookup_asset_symbols_ids(self):
        lcc.set_step("Lookup asset ids")
        params = [["ECHO", "ECHOTEST"]]
        self.send_request(self.get_request(self.__lookup_asset_symbols, params), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check lookup asset ids")
        check_that(
            "'lookup asset ids'",
            self.__resp["result"],
            is_list(self.get_expected(self.__lookup_asset_symbols)),
        )

    @lcc.test("Get order book")
    @lcc.hidden()
    def test_get_order_book(self, base, quote, depth=50):
        pass

    @lcc.test("Get limit orders")
    @lcc.hidden()
    def test_get_limit_orders(self, a, b, limit):
        pass

    @lcc.test("Get call orders")
    @lcc.tags("don't work")
    @lcc.disabled()
    def test_get_call_orders(self):
        lcc.set_step("Get call orders")
        self.send_request(self.get_request(self.__get_call_orders), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get call orders")
        check_that(
            "'call orders'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_call_orders)),
        )

    @lcc.test("Get settle orders")
    @lcc.tags("empty data receive")
    def test_get_settle_orders(self):
        lcc.set_step("Get settle orders")
        self.send_request(self.get_request(self.__get_settle_orders), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get settle orders")
        check_that(
            "'settle orders'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_settle_orders)),
        )

    @lcc.test("Get margin positions")
    @lcc.tags("empty data receive")
    def test_get_margin_positions(self):
        lcc.set_step("Get margin positions")
        self.send_request(self.get_request(self.__get_margin_positions), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get margin positions")
        check_that(
            "'margin positions'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_margin_positions)),
        )

    @lcc.test("Subscribe to market")
    @lcc.hidden()
    def test_subscribe_to_market(self, callback, a, b):
        pass

    @lcc.test("Unsubscribe to market")
    @lcc.hidden()
    def test_unsubscribe_from_market(self, a, b):
        pass

    @lcc.test("Get ticker")
    @lcc.hidden()
    def test_get_ticker(self, base, quote):
        pass

    @lcc.test("Get 24 volume")
    @lcc.hidden()
    def test_get_24_volume(self, base, quote):
        pass

    @lcc.test("Get trade history")
    @lcc.hidden()
    def test_get_trade_history(self, base, quote, start, stop, limit=100):
        pass

    @lcc.test("Get witnesses")
    def test_get_witnesses(self):
        lcc.set_step("Get witnesses")
        self.send_request(self.get_request(self.__get_witnesses), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get witnesses")
        check_that_in(
            self.__resp["result"][0],
            "id", is_str("1.6.0"),
            "witness_account", is_str("1.2.0"),
            "last_aslot", is_integer(),
            "signing_key", is_str("ECHO1111111111111111111111111111111114T1Anm"),
            "pay_vb", is_str("1.13.1"),
            "vote_id", is_str("1:0"),
            "total_votes", is_integer(0),
            "url", is_str(""),
            "total_missed", is_integer(0),
            "last_confirmed_block_num", is_integer(),
            "ed_signing_key", is_str("0000000000000000000000000000000000000000000000000000000000000000")
        )

    @lcc.test("Get witness by account")
    def test_get_witness_by_account(self):
        lcc.set_step("Get witness by account")
        self.send_request(self.get_request(self.__get_witness_by_account), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check witness by account")
        check_that_in(
            self.__resp["result"],
            "id", is_str("1.6.0"),
            "witness_account", is_str("1.2.0"),
            "last_aslot", is_integer(),
            "signing_key", is_str("ECHO1111111111111111111111111111111114T1Anm"),
            "pay_vb", is_str("1.13.1"),
            "vote_id", is_str("1:0"),
            "total_votes", is_integer(0),
            "url", is_str(""),
            "total_missed", is_integer(0),
            "last_confirmed_block_num", is_integer(),
            "ed_signing_key", is_str("0000000000000000000000000000000000000000000000000000000000000000")
        )

    @lcc.test("Check return result methods 'get_witnesses' and 'get_witness_by_account'")
    def test_return_result(self):
        lcc.set_step("Get witnesses use 'get_witnesses'")
        self.send_request(self.get_request(self.__get_witnesses), self.__identifier)
        resp1 = self.get_response()

        lcc.set_step("Get witnesses use 'get_witness_by_account'")
        self.send_request(self.get_request(self.__get_witness_by_account), self.__identifier)
        resp2 = self.get_response()

        lcc.set_step("Check return result methods 'get_witnesses' and 'get_witness_by_account'")
        check_that(
            "test",
            resp1["result"][0], equal_to(resp2["result"])
        )

    @lcc.test("Lookup witness accounts")
    @lcc.hidden()
    def test_lookup_witness_accounts(self, lower_bound_name, limit):
        pass

    @lcc.test("Get witness count")
    def test_get_witness_count(self):
        lcc.set_step("Get witness count")
        self.send_request(self.get_request(self.__get_witness_count), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get witness count")
        check_that(
            "'witness count'",
            self.__resp["result"],
            is_integer(1)
        )

    @lcc.test("Get committee members")
    def test_get_committee_members(self):
        lcc.set_step("Get committee members")
        self.send_request(self.get_request(self.__get_committee_members), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get committee members")
        check_that(
            "'committee members'",
            self.__resp["result"],
            is_list(self.get_expected(self.__get_committee_members)),
        )

    @lcc.test("Get committee members by account")
    def test_get_committee_member_by_account(self):
        lcc.set_step("Get committee members by account")
        self.send_request(self.get_request(self.__get_committee_member_by_account), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get committee members by account")
        check_that(
            "'committee members by account'",
            self.__resp["result"],
            is_dict(self.get_expected(self.__get_committee_member_by_account)),
        )

    @lcc.test("Lookup committee member by accounts")
    @lcc.hidden()
    def test_lookup_committee_member_accounts(self, lower_bound_name, limit):
        pass

    @lcc.test("Get workers by account")
    @lcc.tags("empty data receive")
    def test_get_workers_by_account(self):
        lcc.set_step("Get workers by account")
        self.send_request(self.get_request(self.__get_workers_by_account), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get workers by account")
        check_that(
            "'workers by account'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_workers_by_account)),
        )

    @lcc.test("Lookup vote ids")
    def test_lookup_vote_ids(self):
        lcc.set_step("Lookup vote ids")
        self.send_request(self.get_request(self.__lookup_vote_ids), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check lookup vote ids")
        check_that(
            "'lookup vote ids'",
            self.__resp["result"],
            is_list(self.get_expected(self.__lookup_vote_ids)),
        )

    @lcc.test("Get transaction hex")
    def test_get_transaction_hex(self):
        lcc.set_step("Get transaction hex")
        self.send_request(self.get_request(self.__get_transaction_hex, [self.get_expected(self.__get_transaction)]),
                          self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get transaction hex")
        check_that(
            "'transaction hex'",
            self.__resp["result"],
            is_str(self.get_expected(self.__get_transaction_hex)),
        )

    @lcc.test("Get required signatures")
    def test_get_required_signatures(self):
        lcc.set_step("Get potential signatures")
        self.send_request(self.get_request(self.__get_required_signatures,
                                           [self.get_expected(self.__get_transaction),
                                            ["ECHO6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV"]]),
                          self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get potential signatures")
        check_that(
            "'potential signatures'",
            self.__resp["result"],
            is_list(["ECHO6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV"]),
        )

    @lcc.test("Get potential signatures")
    def test_get_potential_signatures(self):
        lcc.set_step("Get potential signatures")
        self.send_request(self.get_request(self.__get_potential_signatures,
                                           [self.get_expected(self.__get_transaction)]),
                          self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get potential signatures")
        check_that(
            "'potential signatures'",
            self.__resp["result"],
            is_list(self.get_expected(self.__get_potential_signatures)),
        )

    @lcc.test("Get potential address signatures")
    @lcc.tags("empty data receive")
    def test_get_potential_address_signatures(self):
        lcc.set_step("Get potential address signatures")
        self.send_request(self.get_request(self.__get_potential_address_signatures,
                                           [self.get_expected(self.__get_transaction)]),
                          self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get potential address signatures")
        check_that(
            "'potential address signatures'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_potential_address_signatures)),
        )

    @lcc.test("Verify authority")
    def test_verify_authority(self):
        lcc.set_step("Verify authority")
        self.send_request(self.get_request(self.__verify_authority,
                                           [self.get_expected(self.__get_transaction)]),
                          self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check verify authority")
        check_that(
            "'verify authority'",
            self.__resp["result"],
            is_true(),
        )

    @lcc.test("Verify account authority")
    @lcc.tags("don't work")
    @lcc.disabled()
    def test_verify_account_authority(self):
        lcc.set_step("Verify account authority")
        params = ["1.2.12", []]
        self.send_request(self.get_request(self.__verify_account_authority, params), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check verify account authority")
        check_that(
            "'verify account authority'",
            self.__resp["result"],
            is_true(),
        )

    @lcc.test("Validate transaction")
    @lcc.tags("don't work")
    @lcc.disabled()
    def test_validate_transaction(self):
        lcc.set_step("Validate transaction")
        self.send_request(self.get_request(self.__validate_transaction,
                                           [self.get_expected(self.__get_transaction)]),
                          self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check validate transaction")
        check_that(
            "'validate transaction'",
            self.__resp["result"],
            is_true(),
        )

    @lcc.test("Get required fees")
    def test_get_required_fees(self):
        lcc.set_step("Get required fees")
        params = [self.get_expected(self.__contract_operations), "1.3.0"]
        self.send_request(self.get_request(self.__get_required_fees, params), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get required fees")
        check_that(
            "'required fees'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_required_fees)),
        )

    @lcc.test("Get proposed transactions")
    @lcc.tags("empty data receive")
    def test_get_proposed_transactions(self):
        lcc.set_step("Get proposed transactions")
        self.send_request(self.get_request(self.__get_proposed_transactions,), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get proposed transactions")
        check_that(
            "'proposed transactions'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_proposed_transactions)),
        )

    @lcc.test("Get all contracts")
    def test_get_all_contracts(self):
        lcc.set_step("Get all contracts")
        self.send_request(self.get_request(self.__get_all_contracts), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get all contracts")
        check_that(
            "'all contracts'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_all_contracts)),
        )

    @lcc.test("Get contract logs")
    def test_get_contract_logs(self):
        lcc.set_step("Get contract logs")
        self.send_request(self.get_request(self.__get_contract_logs), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get contract logs")
        check_that(
            "'contract logs'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_contract_logs)),
        )

    @lcc.test("Subscribe contract logs")
    @lcc.hidden()
    def test_subscribe_contract_logs(self, callback, contract_id, _from, to):
        pass

    @lcc.test("Get contract result")
    def test_get_contract_result(self):
        lcc.set_step("Get contract result")
        self.send_request(self.get_request(self.__get_contract_result), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get contract result")
        check_that(
            "'contract result'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_contract_result)),
        )

    @lcc.test("Get contract")
    def test_get_contract(self):
        lcc.set_step("Get contract")
        self.send_request(self.get_request(self.__get_contract), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get contract")
        check_that(
            "'contract'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_contract)),
        )

    @lcc.test("Call contract no changing state")
    def test_call_contract_no_changing_state(self):
        lcc.set_step("Get contract")
        self.send_request(self.get_request(self.__call_contract_no_changing_state), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check call contract no changing state")
        check_that(
            "'method call'",
            self.__resp["result"],
            is_str("000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000"
                   "0000000000000000000000000000000e48656c6c6f20576f726c64212121000000000000000000000000000000000000"),
        )

    @lcc.test("Get contracts")
    def test_get_contracts(self):
        lcc.set_step("Get contracts")
        self.send_request(self.get_request(self.__get_contracts), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get contracts")
        check_that(
            "'contracts'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_contracts)),
        )

    @lcc.test("Get contract balances")
    def test_get_contract_balances(self):
        lcc.set_step("Get contract balances")
        self.send_request(self.get_request(self.__get_contract_balances), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get contract balances")
        check_that(
            "'contract balances'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_contract_balances)),
        )

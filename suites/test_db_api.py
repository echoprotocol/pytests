import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_, check_that, check_that_in, is_str, is_integer

from common.utils import BaseTest

SUITE = {
    "description": "Test 'Database API'"
}


@lcc.suite("Test database methods")
class TestDatabaseMethod(BaseTest):
    __get_block = "get_block"
    __get_block_header = "get_block_header"
    __get_block_header_exp = "get_block_header_exp"
    __get_block_exp = "block_exp"
    __get_transaction = "get_transaction"
    __get_transaction_exp = "transaction_exp"
    __get_chain_properties = "get_chain_properties"
    __get_chain_properties_exp = "get_chain_properties_exp"
    __get_global_properties = "get_global_properties"
    __get_global_properties_exp = "get_global_properties_exp"
    __get_config = "get_config"
    __get_config_exp = "get_config_exp"
    __get_chain_id = "get_chain_id"
    __get_chain_id_exp = "get_chain_id_exp"
    __get_dynamic_global_properties = "get_dynamic_global_properties"
    __get_dynamic_global_properties_exp = "get_dynamic_global_properties_exp"
    __get_key_references = "get_key_references"
    __get_key_references_exp = "get_key_references_exp"
    __get_account_by_name = "get_account_by_name"
    __get_account_by_name_exp = "get_account_by_name_exp"
    __get_accounts = "get_accounts"
    __get_accounts_exp = "get_accounts_exp"
    __get_full_accounts = "get_full_accounts"
    __get_full_accounts_ids_exp = "get_full_accounts_ids_exp"
    __get_full_accounts_names_exp = "get_full_accounts_names_exp"
    __get_account_references = "get_account_references"
    __get_account_references_exp = "get_account_references_exp"
    __lookup_account_names = "lookup_account_names"
    __lookup_account_names_exp = "lookup_account_names_exp"
    __lookup_accounts = "lookup_accounts"
    __lookup_accounts_exp = "lookup_accounts_exp"
    __get_account_count = "get_account_count"
    __get_account_balances = "get_account_balances"
    __get_account_balances_exp_empty = "get_account_balances_exp_empty"
    __get_account_balances_exp = "get_account_balances_exp"
    __get_named_account_balances = "get_named_account_balances"
    __get_vested_balances = "get_vested_balances"
    __get_assets = "get_assets"
    __get_assets_exp = "get_assets_exp"
    __list_assets = "list_assets"
    __list_assets_exp = "list_assets_exp"
    __lookup_asset_symbols = "lookup_asset_symbols"
    __lookup_asset_symbols_exp = "lookup_asset_symbols_exp"
    __get_call_orders = "get_call_orders"
    __get_call_orders_exp = "get_call_orders_exp"
    __get_settle_orders = "get_settle_orders"
    __get_settle_orders_exp = "get_settle_orders_exp"
    __get_margin_positions = "get_margin_positions"
    __get_margin_positions_exp = "get_margin_positions_exp"
    __get_witnesses = "get_witnesses"
    __get_witness_by_account = "get_witness_by_account"
    __get_witness_count = "get_witness_count"

    def __init__(self):
        super().__init__()
        self.__resp = None
        self.__identifier = self.get_identifier(self._database_api)

    @lcc.test("Get objects")
    @lcc.hidden()
    def test_get_objects(self, array_ids):
        pass

    @lcc.test("Set subscribe callback")
    @lcc.hidden()
    def test_set_subscribe_callback(self, callback, notify_remove_create):
        pass

    @lcc.test("Set pending transaction callback")
    @lcc.hidden()
    def test_set_pending_transaction_callback(self, callback):
        pass

    @lcc.test("Set block applied callback")
    @lcc.hidden()
    def test_set_block_applied_callback(self, callback):
        pass

    @lcc.test("Cancel all subscriptions")
    @lcc.hidden()
    def test_cancel_all_subscriptions(self):
        pass

    @lcc.test("Get block")
    def test_get_block(self):
        lcc.set_step("Retrieve a full, signed block")
        self.send_request(self.get_request(self.__get_block), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check block info")
        check_that(
            "'block info'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_block_exp)),
        )

    @lcc.test("Get block header")
    def test_get_block_header(self):
        lcc.set_step("Retrieve header of signed block.")
        self.send_request(self.get_request(self.__get_block_header), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check block header info")
        check_that(
            "'block header info'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_block_header_exp)),
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
            is_(self.get_expected(self.__get_transaction_exp)),
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
            is_(self.get_expected(self.__get_chain_properties_exp)),
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
            is_(self.get_expected(self.__get_global_properties_exp)),
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
            is_(self.get_expected(self.__get_config_exp)),
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
            is_(self.get_expected(self.__get_chain_id_exp)),
        )

    @lcc.test("Get dynamic global properties")
    def test_get_dynamic_global_properties(self):
        lcc.set_step("Get dynamic global properties")
        self.send_request(self.get_request(self.__get_dynamic_global_properties), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check dynamic global properties info")
        check_that_in(
            self.__resp["result"],
            "id", is_str(is_("2.1.0")),
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
            is_(self.get_expected(self.__get_key_references_exp)),
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
            is_(self.get_expected(self.__get_accounts_exp)),
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
            is_(self.get_expected(self.__get_full_accounts_ids_exp)),
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
            is_(self.get_expected(self.__get_full_accounts_names_exp)),
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
            is_(self.get_expected(self.__get_account_by_name_exp)),
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
            is_(self.get_expected(self.__get_account_references_exp)),
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
            is_(self.get_expected(self.__lookup_account_names_exp)),
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
            is_(self.get_expected(self.__lookup_accounts_exp)),
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
            is_integer(is_(15))
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
            is_(self.get_expected(self.__get_account_balances_exp_empty)),
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
            is_(self.get_expected(self.__get_account_balances_exp)),
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
            is_(self.get_expected(self.__get_account_balances_exp_empty)),
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
            is_(self.get_expected(self.__get_account_balances_exp)),
        )

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
            is_(self.get_expected(self.__get_account_balances_exp)),
        )

    @lcc.test("Get assets")
    def test_get_assets(self):
        lcc.set_step("Get assets")
        self.send_request(self.get_request(self.__get_assets), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get assets")
        check_that(
            "'assets'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_assets_exp)),
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
            is_(self.get_expected(self.__list_assets_exp)),
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
            is_(self.get_expected(self.__lookup_asset_symbols_exp)),
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
            is_(self.get_expected(self.__lookup_asset_symbols_exp)),
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
            is_(self.get_expected(self.__get_call_orders_exp)),
        )

    @lcc.test("Get settle orders")
    def test_get_settle_orders(self):
        lcc.set_step("Get settle orders")
        self.send_request(self.get_request(self.__get_settle_orders), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get settle orders")
        check_that(
            "'settle orders'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_settle_orders_exp)),
        )

    @lcc.test("Get margin positions")
    def test_get_margin_positions(self):
        lcc.set_step("Get margin positions")
        self.send_request(self.get_request(self.__get_margin_positions), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get margin positions")
        check_that(
            "'margin positions'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_margin_positions_exp)),
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
            "id", is_("1.6.0"),
            "witness_account", is_("1.2.0"),
            "last_aslot", is_integer(),
            "signing_key", is_("ECHO1111111111111111111111111111111114T1Anm"),
            "pay_vb", is_("1.13.0"),
            "vote_id", is_("1:0"),
            "total_votes", is_(0),
            "url", is_(""),
            "total_missed", is_(0),
            "last_confirmed_block_num", is_integer(),
            "ed_signing_key", is_("0000000000000000000000000000000000000000000000000000000000000000")
        )

    @lcc.test("Get witness by account")
    def test_get_witness_by_account(self):
        lcc.set_step("Get witness by account")
        self.send_request(self.get_request(self.__get_witness_by_account), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check witness by account")
        check_that_in(
            self.__resp["result"],
            "id", is_("1.6.0"),
            "witness_account", is_("1.2.0"),
            "last_aslot", is_integer(),
            "signing_key", is_("ECHO1111111111111111111111111111111114T1Anm"),
            "pay_vb", is_("1.13.0"),
            "vote_id", is_("1:0"),
            "total_votes", is_(0),
            "url", is_(""),
            "total_missed", is_(0),
            "last_confirmed_block_num", is_integer(),
            "ed_signing_key", is_("0000000000000000000000000000000000000000000000000000000000000000")
        )

    @lcc.test("Lookup witness accounts")
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
            is_integer(is_(1))
        )

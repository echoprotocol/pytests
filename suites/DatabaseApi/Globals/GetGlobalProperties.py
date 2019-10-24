# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_integer, check_that_in, check_that, is_list, is_, has_length, \
    is_dict, has_entry, is_str

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_global_properties'"
}


@lcc.prop("main", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_globals", "get_global_properties")
@lcc.suite("Check work of method 'get_global_properties'", rank=1)
class GetGlobalProperties(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = None
        self.all_operations = self.echo.config.operation_ids.__dict__
        self.no_fee_count = 0
        self.only_fee_count = 0
        self.fee_with_price_per_kbyte_count = 0
        self.account_create_fee_count = 0
        self.asset_create_count = 0
        self.pool_fee_count = 0

    @staticmethod
    def no_fee(actual_fee):
        check_that("fee", actual_fee, has_length(0))

    @staticmethod
    def only_fee(actual_fee):
        if check_that("fee", actual_fee, has_length(1)):
            check_that_in(
                actual_fee,
                "fee", is_integer(), quiet=True
            )

    @staticmethod
    def fee_with_price_per_kbyte(actual_fee):
        if check_that("fee", actual_fee, has_length(2)):
            check_that_in(
                actual_fee,
                "fee", is_integer(),
                "price_per_kbyte", is_integer(),
                quiet=True
            )

    @staticmethod
    def account_create_fee(actual_fee):
        if check_that("fee", actual_fee, has_length(3)):
            check_that_in(
                actual_fee,
                "basic_fee", is_integer(),
                "premium_fee", is_integer(),
                "price_per_kbyte", is_integer(),
                quiet=True
            )

    @staticmethod
    def asset_create_fee(actual_fee):
        if check_that("fee", actual_fee, has_length(4)):
            check_that_in(
                actual_fee,
                "symbol3", is_integer(),
                "symbol4", is_integer(),
                "long_symbol", is_integer(),
                "price_per_kbyte", is_integer(),
                quiet=True
            )

    @staticmethod
    def pool_fee(actual_fee):
        if check_that("fee", actual_fee, has_length(2)):
            check_that_in(
                actual_fee,
                "fee", is_integer(),
                "pool_fee", is_integer(),
                quiet=True
            )

    def check_default_fee_for_operation(self, current_fees, operations, check_kind):
        for operation in operations:
            for fee in current_fees:
                if fee[0] == self.all_operations.get(operation.upper()):
                    lcc.log_info("Check default fee for '{}' operation, "
                                 "operation_id is '{}'".format(operation, fee[0]))
                    check_kind(fee[1])
                    break

    def show_wrong_fee_operations(self, current_operations_ids, operations_for_checking):
        all_operations_names = [key for key in self.all_operations.keys()]
        all_operations_ids = [value for value in self.all_operations.values()]
        ids, operations, added_operations, wrong_fee_operations = [], [], [], []
        for current_operation_id in current_operations_ids:
            if current_operation_id in all_operations_ids:
                ids.append(current_operation_id)
        for id in ids:
            operations.append(all_operations_names[id].lower())
        for operation in operations:
            if operation not in operations_for_checking:
                added_operations.append(operation)
        if len(added_operations) > 1:
            lcc.log_info("Added operations: {}".format(added_operations))
        for operation in operations_for_checking:
            if operation not in operations:
                wrong_fee_operations.append(operation)
        if len(wrong_fee_operations) > 1:
            lcc.log_info("Wrong fee operations: {}".format(wrong_fee_operations))

    def check_sidechain_config(self, sidechain_config, eth_params, eth_methods):
        if check_that("sidechain_config", sidechain_config, has_length(19)):
            for eth_param in eth_params:
                if not self.type_validator.is_hex(sidechain_config[eth_param]):
                    lcc.log_error(
                        "Wrong format of '{}', got: {}".format(eth_param, sidechain_config[eth_param]))
                else:
                    lcc.log_info("'{}' has correct format: hex".format(eth_param))
            for eth_method in eth_methods:
                if check_that("eth_method", sidechain_config[eth_method], has_length(2)):
                    if not self.type_validator.is_hex(sidechain_config[eth_method]["method"]):
                        lcc.log_error(
                            "Wrong format of '{}', got: {}".format(eth_method, sidechain_config[eth_method]))
                    else:
                        lcc.log_info("'{}' has correct format: hex".format(eth_method))
                    check_that_in(
                        sidechain_config[eth_method], "gas", is_integer(), quiet=True
                    )
            if not self.type_validator.is_eth_asset_id(sidechain_config["ETH_asset_id"]):
                lcc.log_error("Wrong format of 'ETH_asset_id', got: {}".format(sidechain_config["ETH_asset_id"]))
            else:
                lcc.log_info("'ETH_asset_id' has correct format: eth_asset_id")
            if not self.type_validator.is_btc_asset_id(sidechain_config["BTC_asset_id"]):
                lcc.log_error("Wrong format of 'BTC_asset_id', got: {}".format(sidechain_config["BTC_asset_id"]))
            else:
                lcc.log_info("'BTC_asset_id' has correct format: btc_asset_id")
            if check_that("fines", sidechain_config["fines"], has_length(1)):
                check_that_in(
                    sidechain_config["fines"], "generate_eth_address", is_(-10), quiet=True
                )
            check_that_in(
                sidechain_config,
                "satoshis_per_byte", is_integer(),
                "coefficient_waiting_blocks", is_integer(),
                quiet=True)
            self.check_uint64_numbers(sidechain_config, "gas_price", quiet=False)

    def check_erc20_config(self, erc20_config, erc20_methods):
        if check_that("erc20_config", erc20_config, has_length(6)):
            if not self.type_validator.is_hex(erc20_config["contract_code"]):
                lcc.log_error("Wrong format of 'contract_code', got: {}".format(erc20_config["contract_code"]))
            else:
                lcc.log_info("'contract_code' has correct format: hex")
            if not self.type_validator.is_hex(erc20_config["transfer_topic"]):
                lcc.log_error("Wrong format of 'transfer_topic', got: {}".format(erc20_config["transfer_topic"]))
            else:
                lcc.log_info("'transfer_topic' has correct format: hex")
            check_that_in(
                erc20_config, "create_token_fee", is_integer(), quiet=True
            )
            for erc20_method in erc20_methods:
                if check_that("erc20_method", erc20_config[erc20_method], has_length(2)):
                    if not self.type_validator.is_hex(erc20_config[erc20_method]["method"]):
                        lcc.log_error("Wrong format of '{}', got: {}".format(erc20_method, erc20_config[erc20_method]))
                    else:
                        lcc.log_info("'{}' has correct format: hex".format(erc20_method))
                    check_that_in(
                        erc20_config[erc20_method], "gas", is_integer(), quiet=True
                    )

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__api_identifier))

    @lcc.test("Check all fields in global properties")
    def method_main_check(self):
        fee_with_price_per_kbyte_operations = ["account_update", "asset_update", "proposal_create", "proposal_update",
                                               "account_address_create"]
        only_fee_operations = ["transfer", "account_whitelist", "asset_update_bitasset", "balance_freeze",
                               "asset_update_feed_producers", "asset_issue", "asset_reserve", "asset_fund_fee_pool",
                               "asset_publish_feed", "proposal_delete", "committee_member_create",
                               "committee_member_update", "committee_member_update_global_parameters",
                               "vesting_balance_create", "vesting_balance_withdraw", "override_transfer",
                               "asset_claim_fees", "contract_create", "contract_call",
                               "transfer_to_address", "contract_update",
                               "sidechain_eth_create_address", "sidechain_eth_deposit", "sidechain_eth_withdraw",
                               "sidechain_eth_approve_withdraw", "contract_fund_pool", "contract_whitelist",
                               "sidechain_erc20_deposit_token", "sidechain_erc20_withdraw_token",
                               "sidechain_erc20_approve_token_withdraw",
                               'committee_member_activate', 'committee_member_deactivate',
                               'committee_frozen_balance_deposit', 'committee_frozen_balance_withdraw',
                               'sidechain_eth_approve_address', 'sidechain_issue', 'sidechain_burn',
                               'sidechain_erc20_issue', 'sidechain_erc20_burn', 'sidechain_btc_create_address',
                               'sidechain_btc_create_intermediate_deposit', 'sidechain_btc_intermediate_deposit',
                               'sidechain_btc_deposit', 'sidechain_btc_withdraw', 'sidechain_btc_approve_withdraw',
                               'sidechain_btc_aggregate']
        no_fee_operations = ["balance_claim", "balance_unfreeze", 'contract_internal_create', 'contract_internal_call',
                             'contract_selfdestruct', 'block_reward']
        account_create_fee_operations = ["account_create"]
        asset_create_fee_operations = ["asset_create"]
        pool_fee_operations = ["sidechain_erc20_register_token"]

        lcc.set_step("Get global properties")
        response_id = self.send_request(self.get_request("get_global_properties"), self.__api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_global_properties'")

        lcc.set_step("Check main fields")
        if check_that("global_properties", response["result"], has_length(4)):
            if not self.type_validator.is_global_object_id(response["result"]["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(response["result"]["id"]))
            else:
                lcc.log_info("'id' has correct format: global_property_object_type")
            check_that_in(
                response["result"],
                "parameters", is_dict(),
                "next_available_vote_id", is_integer(),
                "active_committee_members", is_list(),
                quiet=True
            )

        lcc.set_step("Check global parameters: 'current_fees' field")
        parameters = response["result"]["parameters"]
        if check_that("parameters", parameters, has_length(29)):
            check_that_in(
                parameters,
                "current_fees", is_dict(),
                "maintenance_interval", is_integer(),
                "maintenance_duration_seconds", is_integer(),
                "committee_proposal_review_period", is_integer(),
                "maximum_transaction_size", is_integer(),
                "maximum_block_size", is_integer(),
                "maximum_time_until_expiration", is_integer(),
                "maximum_proposal_lifetime", is_integer(),
                "maximum_asset_whitelist_authorities", is_integer(),
                "maximum_asset_feed_publishers", is_integer(),
                "maximum_committee_count", is_integer(),
                "maximum_authority_membership", is_integer(),
                "reserve_percent_of_fee", is_integer(),
                "network_percent_of_fee", is_integer(),
                "max_predicate_opcode", is_integer(),
                "accounts_per_fee_scale", is_integer(),
                "account_fee_scale_bitshifts", is_integer(),
                "account_fee_scale_bitshifts", is_integer(),
                "max_authority_depth", is_integer(),
                "block_producer_reward_ratio", is_integer(),
                "block_emission_amount", is_integer(),
                "frozen_balances_multipliers", is_list(),
                "committee_frozen_balance_to_activate", is_str(),
                "committee_maintenance_intervals_to_deposit", is_integer(),
                "committee_freeze_duration_seconds", is_integer(),
                "echorand_config", is_dict(),
                "sidechain_config", is_dict(),
                "erc20_config", is_dict(),
                "gas_price", is_dict(),
                "extensions", is_list(),
                quiet=True
            )

        lcc.set_step("Check global parameters: 'current_fees' field")
        current_fees = parameters["current_fees"]
        if check_that("current_fees", current_fees, has_length(2)):
            check_that_in(
                current_fees,
                "parameters", is_list(),
                "scale", is_integer(),
                quiet=True
            )

        lcc.set_step("Check global parameters: 'frozen_balances_multipliers' field")
        frozen_balances_multipliers = parameters["frozen_balances_multipliers"]
        for frozen_balance in frozen_balances_multipliers:
            for balance in frozen_balance:
                check_that("frozen_balance", balance, is_integer())

        # todo: uncomment when current_fees of btc operations will be added
        # lcc.set_step("Check the count of fees for operations")
        # fee_parameters = current_fees["parameters"]
        # require_that(
        #     "count of fees for operations",
        #     fee_parameters, has_length(len(self.all_operations))
        # )

        # lcc.set_step("Check that count of checking fees fields equal to all operations")
        # checking_operations_fee_types = [fee_with_price_per_kbyte_operations, only_fee_operations, no_fee_operations,
        #                                  account_create_fee_operations, asset_create_fee_operations,
        #                                  pool_fee_operations]
        # for fee_type in checking_operations_fee_types:
        #     all_checking_operations.extend(fee_type)
        # check_that("'length of checking fees fields equal to all operations'", all_checking_operations,
        #            has_length(len(self.all_operations)))

        fee_with_price_per_kbyte_operations_ids, only_fee_operations_ids, no_fee_operations_ids, \
        account_create_fee_operations_ids, asset_create_fee_operations_ids, pool_fee_operations_ids = [], [], [], [], \
                                                                                                      [], []

        lcc.set_step("Save the number of types of current_fees")
        fee_parameters = current_fees["parameters"]
        for fee_parameter in fee_parameters:
            parameter = fee_parameter[1]
            if len(parameter) == 0:
                no_fee_operations_ids.append(fee_parameter[0])
                self.no_fee_count += 1
                continue
            if len(parameter) == 1 and "fee" in parameter:
                self.only_fee_count += 1
                only_fee_operations_ids.append(fee_parameter[0])
                continue
            if len(parameter) == 2 and ("fee" and "price_per_kbyte") in parameter:
                fee_with_price_per_kbyte_operations_ids.append(fee_parameter[0])
                self.fee_with_price_per_kbyte_count += 1
                continue
            if len(parameter) == 2 and ("membership_annual_fee" and "membership_lifetime_fee") in parameter:
                only_fee_operations_ids.append(fee_parameter[0])
                self.account_update_fee_count += 1
                continue
            if len(parameter) == 2 and ("fee" and "pool_fee") in parameter:
                account_create_fee_operations_ids.append(fee_parameter[0])
                self.pool_fee_count += 1
                continue
            if len(parameter) == 3 and ("basic_fee" and "premium_fee" and "price_per_kbyte") in parameter:
                account_create_fee_operations_ids.append(fee_parameter[0])
                self.account_create_fee_count += 1
                continue
            if len(parameter) == 4 and (
                    "symbol3" and "symbol4" and "long_symbol" and "price_per_kbyte") in parameter:
                asset_create_fee_operations_ids.append(fee_parameter[0])
                self.asset_create_count += 1
                continue
            else:
                lcc.log_warning("Warn: Added new option for calculating fee for the operation, got: '{}'".format(
                    fee_parameter))

        lcc.set_step("Check 'fee_with_price_per_kbyte' for operations")
        check_that("'fee_with_price_per_kbyte' operation count", fee_with_price_per_kbyte_operations,
                   has_length(self.fee_with_price_per_kbyte_count))
        self.check_default_fee_for_operation(fee_parameters, fee_with_price_per_kbyte_operations,
                                             self.fee_with_price_per_kbyte)
        self.show_wrong_fee_operations(fee_with_price_per_kbyte_operations_ids, fee_with_price_per_kbyte_operations)

        lcc.set_step("Check 'only_fee' for operations")
        check_that("'only_fee' operation count", only_fee_operations, has_length(self.only_fee_count))
        self.check_default_fee_for_operation(fee_parameters, only_fee_operations, self.only_fee)
        self.show_wrong_fee_operations(only_fee_operations_ids, only_fee_operations)

        lcc.set_step("Check 'no_fee' for operations")
        check_that("'no_fee' operation count", no_fee_operations, has_length(self.no_fee_count))
        self.check_default_fee_for_operation(fee_parameters, no_fee_operations, self.no_fee)
        self.show_wrong_fee_operations(no_fee_operations_ids, no_fee_operations)

        lcc.set_step("Check 'account_create_fee' for operations")
        check_that("'account_create_fee' operation count", account_create_fee_operations,
                   has_length(self.account_create_fee_count))
        self.check_default_fee_for_operation(fee_parameters, account_create_fee_operations,
                                             self.account_create_fee)
        self.show_wrong_fee_operations(account_create_fee_operations_ids, account_create_fee_operations)

        lcc.set_step("Check 'asset_create_fee' for operations")
        check_that("'asset_create_fee' operation count", asset_create_fee_operations,
                   has_length(self.asset_create_count))
        self.check_default_fee_for_operation(fee_parameters, asset_create_fee_operations, self.asset_create_fee)
        self.show_wrong_fee_operations(asset_create_fee_operations_ids, asset_create_fee_operations)

        lcc.set_step("Check 'pool_fee' for operations")
        check_that("'pool_fee' operation count", pool_fee_operations,
                   has_length(self.pool_fee_count))
        if not self.check_default_fee_for_operation(fee_parameters, pool_fee_operations, self.pool_fee):
            self.show_wrong_fee_operations(pool_fee_operations_ids, pool_fee_operations)

        lcc.set_step("Check global parameters: 'echorand_config' field")
        echorand_config = parameters["echorand_config"]
        if check_that("echorand_config", echorand_config, has_length(8)):
            check_that_in(
                echorand_config,
                "_time_net_1mb", is_integer(),
                "_time_net_256b", is_integer(),
                "_creator_count", is_integer(),
                "_verifier_count", is_integer(),
                "_ok_threshold", is_integer(),
                "_max_bba_steps", is_integer(),
                "_gc1_delay", is_integer(),
                "_time_generate", is_integer(),
                quiet=True
            )

        lcc.set_step("Check global parameters: 'sidechain_config' field")
        sidechain_config = parameters["sidechain_config"]
        eth_params = ["eth_contract_address", "eth_committee_updated_topic", "eth_gen_address_topic",
                      "eth_deposit_topic", "eth_withdraw_topic", "erc20_deposit_topic", "erc20_withdraw_topic"]
        eth_methods = ["eth_committee_update_method", "eth_gen_address_method", "eth_withdraw_method",
                       "eth_update_addr_method", "eth_withdraw_token_method", "eth_collect_tokens_method"]
        self.check_sidechain_config(sidechain_config, eth_params, eth_methods)

        lcc.set_step("Check global parameters: 'erc20_config' field")
        erc20_config = parameters["erc20_config"]
        erc20_methods = ["check_balance_method", "burn_method", "issue_method"]
        self.check_erc20_config(erc20_config, erc20_methods)

        lcc.set_step("Check global parameters: 'gas_price' field")
        gas_price = parameters["gas_price"]
        if check_that("gas_price", gas_price, has_length(2)):
            check_that_in(
                gas_price,
                "price", is_integer(),
                "gas_amount", is_integer(),
                quiet=True
            )


@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_globals", "get_global_properties")
@lcc.suite("Negative testing of method 'get_global_properties'", rank=2)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__api_identifier))

    @lcc.test("Call method with params of all types")
    @lcc.tags("Bug: 'ECHO-680'")
    @lcc.depends_on("DatabaseApi.Globals.GetGlobalProperties.GetGlobalProperties.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            # todo: remove if. Bug: "ECHO-680"
            if i == 4:
                continue
            response_id = self.send_request(self.get_request("get_global_properties", random_values[i]),
                                            self.__api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_global_properties' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True
            )

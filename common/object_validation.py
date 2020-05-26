# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import has_length, is_integer, check_that_in, check_that, is_dict, is_list, \
    is_str, is_, is_bool, greater_than, greater_than_or_equal_to, is_in, require_that, equal_to

from common.type_validation import TypeValidator


class ObjectValidator(object):

    def __init__(self):
        self.type_validator = TypeValidator()

    def validate_account_object(self, base_test, account_info):
        if check_that(
                "account info",
                account_info, has_length(16),
                quiet=True
        ):
            check_that_in(
                account_info,
                "active", is_dict(),
                "active_delegate_share", is_integer(),
                "options", is_dict(),
                "whitelisting_accounts", is_list(),
                "blacklisting_accounts", is_list(),
                "whitelisted_accounts", is_list(),
                "blacklisted_accounts", is_list(),
                "active_special_authority", is_list(),
                "top_n_control_flags", is_integer(),
                "accumulated_reward", is_list(),
                "extensions", is_list(),
                quiet=True
            )
            if not base_test.type_validator.is_account_id(account_info["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(account_info["id"]))
            else:
                lcc.log_info("'id' has correct format: account_object_type")
            if not base_test.type_validator.is_account_id(account_info["registrar"]):
                lcc.log_error("Wrong format of 'registrar', got: {}".format(account_info["registrar"]))
            else:
                lcc.log_info("'registrar' has correct format: account_object_type")
            if not base_test.type_validator.is_account_name(account_info["name"]):
                lcc.log_error("Wrong format of 'name', got: {}".format(account_info["name"]))
            else:
                lcc.log_info("'name' has correct format: account_name")
            if not base_test.type_validator.is_echorand_key(account_info["echorand_key"]):
                lcc.log_error("Wrong format of 'echorand_key', got: {}".format(account_info["echorand_key"]))
            else:
                lcc.log_info("'echorand_key' has correct format: echo_rand_key")
            if not base_test.type_validator.is_account_statistics_id(account_info["statistics"]):
                lcc.log_error("Wrong format of 'statistics', got: {}".format(account_info["statistics"]))
            else:
                lcc.log_info("'statistics' has correct format: account_statistics_object_type")

            lcc.set_step("Check 'active' field")
            if check_that(
                    "active",
                    account_info["active"], has_length(3),
                    quiet=True
            ):
                check_that_in(
                    account_info["active"],
                    "weight_threshold", is_integer(),
                    "account_auths", is_list(),
                    "key_auths", is_list(),
                    quiet=True
                )

            lcc.set_step("Check 'options' field")
            if check_that(
                    "options",
                    account_info["options"], has_length(3),
                    quiet=True
            ):
                delegating_account = account_info["options"]["delegating_account"]
                if not base_test.type_validator.is_account_id(delegating_account):
                    lcc.log_error("Wrong format of 'delegating_account', got: {}".format(delegating_account))
                else:
                    lcc.log_info("'{}' has correct format: account_object_type".format(delegating_account))
                check_that_in(
                    account_info["options"],
                    "delegate_share", is_integer(),
                    "extensions", is_list(),
                    quiet=True
                )

    def validate_asset_object(self, base_test, asset):

        def validate_core_exchange_rate_structure(base_test, core_exchange_rate):
            check_that_in(
                core_exchange_rate,
                "base", is_dict(),
                "quote", is_dict(),
                quiet=True
            )
            for key in core_exchange_rate:
                core_exchange_rate_part = core_exchange_rate[key]
                base_test.check_uint64_numbers(
                    core_exchange_rate_part,
                    "amount",
                    quiet=True
                )
                if not base_test.type_validator.is_asset_id(core_exchange_rate_part["asset_id"]):
                    lcc.log_error("Wrong format of {} 'asset_id', got: {}".format(
                        key, core_exchange_rate_part["asset_id"]))
                else:
                    lcc.log_info("{} 'asset_id' has correct format: asset_id".format(key))

        if check_that(
                "'length of chain asset'",
                asset, has_length(7),
                quiet=True
        ):
            if not base_test.type_validator.is_asset_id(asset["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(asset["id"]))
            else:
                lcc.log_info("'id' has correct format: asset_id")
            if not base_test.type_validator.is_dynamic_asset_data_id(asset["dynamic_asset_data_id"]):
                lcc.log_error("Wrong format of 'dynamic_asset_data_id', got: {}".format(
                    asset["dynamic_asset_data_id"]))
            else:
                lcc.log_info("'dynamic_asset_data_id' has correct format: dynamic_asset_data_id")

            if not base_test.type_validator.is_account_id(asset["issuer"]):
                lcc.log_error("Wrong format of 'issuer', got: {}".format(asset["issuer"]))
            else:
                lcc.log_info("'issuer' has correct format: account_id")
            if not base_test.type_validator.is_asset_name(asset["symbol"]):
                lcc.log_error("Wrong format of 'symbol', got: {}".format(asset["symbol"]))
            else:
                lcc.log_info("'symbol' has correct format: asset_name")
            check_that_in(
                asset,
                "options", is_dict(),
                "extensions", is_list(),
                "precision", is_integer(8),
                quiet=True
            )
            options = asset["options"]
            if check_that(
                    "'options'",
                    options, has_length(8),
                    quiet=True
            ):
                check_that_in(
                    options,
                    "blacklist_authorities", is_list(),
                    "core_exchange_rate", is_dict(),
                    "description", is_str(),
                    "extensions", is_list(),
                    "flags", is_integer(),
                    "issuer_permissions", is_integer(),
                    "whitelist_authorities", is_list(),
                    quiet=True
                )
                core_exchange_rate = options["core_exchange_rate"]
                if check_that(
                        "'core_exchange_rate'",
                        core_exchange_rate, has_length(2),
                        quiet=True
                ):
                    validate_core_exchange_rate_structure(base_test, core_exchange_rate)
                base_test.check_uint64_numbers(
                    options,
                    "max_supply",
                    quiet=True
                )

    def validate_committee_member_object(self, base_test, committee_member):
        if check_that(
                "'committee member'",
                committee_member, has_length(6),
                quiet=True
        ):
            if not base_test.type_validator.is_committee_member_id(committee_member["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(committee_member["id"]))
            else:
                lcc.log_info("'id' has correct format: committee_member_object_type")
            if not base_test.type_validator.is_account_id(committee_member["committee_member_account"]):
                lcc.log_error("Wrong format of 'committee_member_account', got: {}".format(
                    committee_member["committee_member_account"]))
            else:
                lcc.log_info("'committee_member_account' has correct format: account_object_type")
            if not base_test.type_validator.is_eth_address(committee_member["eth_address"]):
                lcc.log_error(
                    "Wrong format of 'eth_address', got: {}".format(committee_member["eth_address"]))
            else:
                lcc.log_info("'eth_address' has correct format: hex")
            if not base_test.type_validator.is_btc_public_key(committee_member["btc_public_key"]):
                lcc.log_error(
                    "Wrong format of 'btc_public_key', got: {}".format(committee_member["btc_public_key"]))
            else:
                lcc.log_info("'eth_address' has correct format: hex")
            check_that_in(
                committee_member,
                "url", is_str(),
                "extensions", is_list(),
                quiet=True
            )

    def validate_proposal_object(self, base_test, proposal_object):
        if check_that(
                "'proposal'",
                proposal_object, has_length(7),
                quiet=True
        ):
            if not base_test.type_validator.is_proposal_id(proposal_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(proposal_object["id"]))
            else:
                lcc.log_info("'id' has correct format: proposal_object_type")
            if not base_test.type_validator.is_iso8601(proposal_object["expiration_time"]):
                lcc.log_error("Wrong format of 'expiration_time', got: {}".format(
                    proposal_object["expiration_time"]))
            else:
                lcc.log_info("'expiration_time' has correct format: iso8601")
            proposed_transaction = proposal_object["proposed_transaction"]
            if check_that(
                    "'proposed transaction'",
                    proposed_transaction, has_length(5),
                    quiet=True
            ):
                if not base_test.type_validator.is_iso8601(proposed_transaction["expiration"]):
                    lcc.log_error("Wrong format of 'expiration', got: {}".format(
                        proposed_transaction["expiration"]))
                else:
                    lcc.log_info("'expiration' has correct format: iso8601")

                check_that_in(
                    proposed_transaction,
                    "ref_block_num", is_integer(0),
                    "ref_block_prefix", is_integer(0),
                    "operations", is_list(),
                    "extensions", is_list(),
                    quiet=True
                )

            check_that_in(
                proposal_object,
                "required_active_approvals", is_list(),
                "available_active_approvals", is_list(),
                "available_key_approvals", is_list(),
                "extensions", is_list(),
                quiet=True
            )

    def validate_operation_history_object(self, base_test, operation_history_object):
        if check_that(
                "operation history",
                operation_history_object, has_length(8),
                quiet=True
        ):
            if not base_test.type_validator.is_operation_history_id(operation_history_object["id"]):
                lcc.log_error("Wrong format of 'operation history id', got: {}".format(
                    operation_history_object["id"]))
            else:
                lcc.log_info("'operation_history_id' has correct format: operation_history_id")
            if not base_test.type_validator.is_operation_id(operation_history_object["op"][0]):
                lcc.log_error("Wrong format of 'operation_id', got: {}".format(operation_history_object["op"][0]))
            else:
                lcc.log_info("'operation_id' has correct format: operation_id")

            check_that_in(
                operation_history_object,
                "op", is_list(),
                "result", is_list(),
                "block_num", is_integer(),
                "trx_in_block", is_integer(),
                "op_in_trx", is_integer(),
                "virtual_op", is_integer(),
                quiet=True
            )

    def validate_vesting_balance_object(self, base_test, vesting_balance_object):
        if check_that(
                "vesting balance",
                vesting_balance_object, has_length(5),
                quiet=True
        ):
            if not base_test.type_validator.is_vesting_balance_id(vesting_balance_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(vesting_balance_object["id"]))
            else:
                lcc.log_info("'id' has correct format: vesting_balance_object_type")
            balance = vesting_balance_object["balance"]
            if check_that(
                    "balance",
                    balance, has_length(2),
                    quiet=True
            ):
                base_test.check_uint256_numbers(balance, "amount", quiet=True)
                if not base_test.type_validator.is_asset_id(balance["asset_id"]):
                    lcc.log_error("Wrong format of 'asset_id', got: {}".format(vesting_balance_object["asset_id"]))
                else:
                    lcc.log_info("'asset_id' has correct format: asset_object_type")
            policy = vesting_balance_object["policy"]
            if check_that(
                    "policy",
                    policy, has_length(2),
                    quiet=True
            ):
                first_element = policy[0]
                second_element = policy[1]
                # todo: first_element='0' - come from bitshares. Remove when corrected in Echo
                check_that(
                    "first element",
                    first_element, is_(0),
                    quiet=True
                )
                if not base_test.type_validator.is_iso8601(second_element["begin_timestamp"]):
                    lcc.log_error(
                        "Wrong format of 'begin_timestamp', got: {}".format(second_element["begin_timestamp"]))
                else:
                    lcc.log_info("'begin_timestamp' has correct format: iso8601")
                check_that_in(
                    second_element,
                    "vesting_cliff_seconds", is_integer(),
                    "vesting_duration_seconds", is_integer(),
                    "begin_balance", is_integer(),
                    quiet=True
                )
                base_test.check_uint256_numbers(
                    second_element,
                    "begin_balance",
                    quiet=True
                )

    def validate_balance_object(self, base_test, balance_object):
        if check_that(
                "balance",
                balance_object, has_length(5),
                quiet=True
        ):
            if not base_test.type_validator.is_balance_id(balance_object["id"]):
                lcc.log_error("Wrong format of 'balance_id', got: {}".format(balance_object["id"]))
            else:
                lcc.log_info("'balance_id' has correct format: balance_id")
            if not base_test.type_validator.is_iso8601(balance_object["last_claim_date"]):
                lcc.log_error(
                    "Wrong format of 'last_claim_date', got: {}".format(balance_object["last_claim_date"]))
            else:
                lcc.log_info("'last_claim_date' has correct format: iso8601")
            base_test.check_uint256_numbers(
                balance_object["balance"],
                "amount",
                quiet=True
            )
            if not base_test.type_validator.is_asset_id(balance_object["balance"]["asset_id"]):
                lcc.log_error(
                    "Wrong format of 'asset_id', got: {}".format(balance_object["balance"]["asset_id"]))
            else:
                lcc.log_info("'asset_id' has correct format: asset_object_type")
            check_that_in(
                balance_object,
                "extensions", is_list(),
                quiet=True
            )

    def validate_frozen_balance_object(self, base_test, frozen_balance_object):
        if check_that(
                "frozen balance",
                frozen_balance_object, has_length(6),
                quiet=True
        ):
            check_that_in(
                frozen_balance_object,
                "owner", is_str(),
                "balance", is_dict(),
                "multiplier", is_integer(),
                "extensions", is_list(),
                quiet=True
            )
            balance = frozen_balance_object["balance"]
            if check_that(
                    "balance",
                    balance, has_length(2),
                    quiet=True
            ):
                check_that(
                    "committee_frozen_balance_amount",
                    int(balance["amount"]), is_integer(),
                    quiet=True
                )
                if not base_test.type_validator.is_asset_id(balance["asset_id"]):
                    lcc.log_error("Wrong format of 'asset_id', got: {}".format(balance["asset_id"]))
                else:
                    lcc.log_info("'asset_id' has correct format")
            if not base_test.type_validator.is_frozen_balance_id(frozen_balance_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(frozen_balance_object["id"]))
            else:
                lcc.log_info("'id' has correct format: frozen_balance_type")
            if not base_test.type_validator.is_iso8601(frozen_balance_object["unfreeze_time"]):
                lcc.log_error("Wrong format of 'unfreeze_time', got: {}".format(
                    frozen_balance_object["unfreeze_time"]))
            else:
                lcc.log_info("'unfreeze_time' has correct format: iso8601")

    def validate_committee_frozen_balance_object(self, base_test, committee_frozen_balance_object):
        lcc.log_info("{}".format(committee_frozen_balance_object))
        if check_that(
                "committee frozen balance",
                committee_frozen_balance_object, has_length(is_in([4, 5])),
                quiet=True
        ):
            balance = committee_frozen_balance_object["balance"]
            if check_that(
                    "balance",
                    balance, has_length(2),
                    quiet=True
            ):
                check_that(
                    "committee_frozen_balance_amount",
                    int(balance["amount"]), is_integer(),
                    quiet=True
                )
                if not base_test.type_validator.is_asset_id(balance["asset_id"]):
                    lcc.log_error("Wrong format of 'asset_id', got: {}".format(
                        committee_frozen_balance_object["asset_id"]))
                else:
                    lcc.log_info("'asset_id' has correct format")
            if not base_test.type_validator.is_committee_frozen_balance_id(committee_frozen_balance_object["id"]):
                lcc.log_error("Wrong format of 'committee_frozen_balance_id', got: {}".format(
                    committee_frozen_balance_object["id"]))
            else:
                lcc.log_info("'committee_frozen_balance_id' has correct format")
            if not base_test.type_validator.is_committee_member_id(committee_frozen_balance_object["owner"]):
                lcc.log_error("Wrong format of 'committee_member_id', got: {}".format(
                    committee_frozen_balance_object["owner"]))
            else:
                lcc.log_info("'committee_member_id' has correct format")
            if len(committee_frozen_balance_object) == 5:
                if not base_test.type_validator.is_iso8601(committee_frozen_balance_object["unfreeze_balance_time"]):
                    lcc.log_error("Wrong format of 'unfreeze_balance_time', got {}".format(
                        committee_frozen_balance_object["unfreeze_balance_time"]))
                else:
                    lcc.log_info("'unfreeze_balance_time' has correct format")

    def validate_contract_object(self, base_test, contract_object):
        if check_that(
                "contract",
                contract_object, has_length(8),
                quiet=True
        ):
            if not base_test.type_validator.is_contract_id(contract_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(contract_object["id"]))
            else:
                lcc.log_info("'id' has correct format: contract_object_type")
            if not base_test.type_validator.is_contract_statistics_id(contract_object["statistics"]):
                lcc.log_error("Wrong format of 'statistics', got: {}".format(contract_object["statistics"]))
            else:
                lcc.log_info("'statistics' has correct format: contract_statistics_object_type")
            if not base_test.type_validator.is_asset_id(contract_object["supported_asset_id"]):
                lcc.log_error("Wrong format of 'supported_asset_id', got {}".format(
                    contract_object["supported_asset_id"]))
            else:
                lcc.log_info("'supported_asset_id' has correct format")
            if not base_test.type_validator.is_account_id(contract_object["owner"]):
                lcc.log_error("Wrong format of 'owner', got {}".format(contract_object["owner"]))
            else:
                lcc.log_info("'owner' has correct format: account id")
            check_that_in(
                contract_object,
                "destroyed", is_bool(),
                "type", is_str(),
                "extensions", is_list(),
                "eth_accuracy", is_bool(),
                quiet=True
            )

    def validate_contract_result_object(self, base_test, contract_result_object):
        if check_that(
                "contract result",
                contract_result_object, has_length(5),
                quiet=True
        ):
            if not base_test.type_validator.is_contract_result_id(contract_result_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(contract_result_object["id"]))
            else:
                lcc.log_info("'id' has correct format: contract_result_object_type")
            check_that_in(
                contract_result_object,
                "type", is_str(),
                "block_num", is_integer(),
                "contracts_id", is_list(),
                "extensions", is_list(),
                quiet=True
            )
            contracts_id = contract_result_object["contracts_id"]
            for contract_id in contracts_id:
                if not base_test.type_validator.is_contract_id(contract_id):
                    lcc.log_error("Wrong format of 'contract_id', got: {}".format(contract_id))
                else:
                    lcc.log_info("'contract_id' has correct format: contract_object_type")

    def validate_eth_address_object(self, base_test, eth_address_object):
        if check_that(
                "account eth address",
                eth_address_object, has_length(7),
                quiet=True
        ):
            if not base_test.type_validator.is_eth_address_id(eth_address_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(eth_address_object["id"]))
            else:
                lcc.log_info("'id' has correct format: eth_address_object_type")
            if not base_test.type_validator.is_account_id(eth_address_object["account"]):
                lcc.log_error("Wrong format of 'account', got: {}".format(eth_address_object["account"]))
            else:
                lcc.log_info("'account' has correct format: account_object_type")
            if not base_test.type_validator.is_hex(eth_address_object["eth_addr"]):
                lcc.log_error("Wrong format of 'eth_addr', got: {}".format(eth_address_object["eth_addr"]))
            else:
                lcc.log_info("'eth_addr' has correct format: hex")
            if not base_test.type_validator.is_hex(eth_address_object["transaction_hash"]):
                lcc.log_error("Wrong format of 'transaction_hash', got: {}".format(
                    eth_address_object["transaction_hash"]))
            else:
                lcc.log_info("'transaction_hash' has correct format: hex")
            check_that_in(
                eth_address_object,
                "is_approved", is_bool(),
                "approves", is_list(),
                "extensions", is_list(),
                quiet=True
            )

    def validate_deposit_eth_object(self, base_test, deposit_eth_object):
        if check_that(
                "'deposit eth'",
                deposit_eth_object, has_length(10),
                quiet=True
        ):
            if not base_test.type_validator.is_deposit_eth_id(deposit_eth_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(deposit_eth_object["id"]))
            else:
                lcc.log_info("'id' has correct format: deposit_eth_object_type")
            if not base_test.type_validator.is_account_id(deposit_eth_object["account"]):
                lcc.log_error("Wrong format of 'account', got: {}".format(deposit_eth_object["account"]))
            else:
                lcc.log_info("'account' has correct format: account_id")
            if not base_test.type_validator.is_hex(deposit_eth_object["transaction_hash"]):
                lcc.log_error("Wrong format of 'transaction_hash', got: {}".format(
                    deposit_eth_object["transaction_hash"]))
            else:
                lcc.log_info("'transaction_hash' has correct format: hex")
            check_that_in(
                deposit_eth_object,
                "deposit_id", greater_than(0),
                "is_approved", is_bool(),
                "is_sent", is_bool(),
                "approves", is_list(),
                "echo_block_number", is_integer(),
                "extensions", is_list(),
                quiet=True
            )

    def validate_withdraw_eth_object(self, base_test, withdraw_eth_object):
        if check_that(
                "'withdraw eth'",
                withdraw_eth_object, has_length(12),
                quiet=True
        ):
            if not base_test.type_validator.is_withdraw_eth_id(withdraw_eth_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(withdraw_eth_object["id"]))
            else:
                lcc.log_info("'id' has correct format: withdraw_eth_object_type")
            if not base_test.type_validator.is_eth_address(withdraw_eth_object["eth_addr"]):
                lcc.log_error("Wrong format of 'eth_addr', got: {}".format(withdraw_eth_object["eth_addr"]))
            else:
                lcc.log_info("'eth_addr' has correct format: ethereum_address_type")
            if not base_test.type_validator.is_account_id(withdraw_eth_object["account"]):
                lcc.log_error("Wrong format of 'account', got: {}".format(withdraw_eth_object["account"]))
            else:
                lcc.log_info("'account' has correct format: account_id")
            if not base_test.type_validator.is_hex(withdraw_eth_object["transaction_hash"]):
                lcc.log_error("Wrong format of 'transaction_hash', got: {}".format(
                    withdraw_eth_object["transaction_hash"]))
            else:
                lcc.log_info("'transaction_hash' has correct format: hex")
            check_that_in(
                withdraw_eth_object,
                "withdraw_id", greater_than_or_equal_to(0),
                "is_approved", is_bool(),
                "is_sent", is_bool(),
                "approves", is_list(),
                "fee", is_integer(),
                "echo_block_number", is_integer(),
                "extensions", is_list()
            )
            if not base_test.type_validator.is_digit(withdraw_eth_object["value"]):
                lcc.log_error("Wrong format of 'value', got: {}".format(withdraw_eth_object["value"]))
            else:
                lcc.log_info("'value' has correct format: digit")

    def validate_erc20_token_object(self, base_test, erc20_token_object):
        if check_that(
                "'erc20 token'",
                erc20_token_object, has_length(8),
                quiet=True
        ):
            if not base_test.type_validator.is_erc20_object_id(erc20_token_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(erc20_token_object["id"]))
            else:
                lcc.log_info("'id' has correct format: erc20_token_object_type")
            if not base_test.type_validator.is_account_id(erc20_token_object["owner"]):
                lcc.log_error("Wrong format of 'owner', got: {}".format(erc20_token_object["owner"]))
            else:
                lcc.log_info("'owner' has correct format: account_id_object_type")
            if not base_test.type_validator.is_eth_address(erc20_token_object["eth_addr"]):
                lcc.log_error("Wrong format of 'eth_addr', got: {}".format(erc20_token_object["eth_addr"]))
            else:
                lcc.log_info("'eth_addr' has correct format: ethereum_address_type")
            if not base_test.type_validator.is_contract_id(erc20_token_object["contract"]):
                lcc.log_error("Wrong format of 'contract', got: {}".format(erc20_token_object["contract"]))
            else:
                lcc.log_info("'contract' has correct format: contract_object_type")
            check_that_in(
                erc20_token_object,
                "name", is_str(),
                "symbol", is_str(),
                "decimals", is_integer(),
                "extensions", is_list(),
                quiet=True
            )

    def validate_erc20_deposit_object(self, base_test, erc20_deposit_object):
        if check_that(
                "'erc20 deposit'",
                erc20_deposit_object, has_length(10),
                quiet=True
        ):
            if not base_test.type_validator.is_deposit_erc20_id(erc20_deposit_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(erc20_deposit_object["id"]))
            else:
                lcc.log_info("'id' has correct format: deposit_erc20_token_object")
            if not base_test.type_validator.is_hex(erc20_deposit_object["transaction_hash"]):
                lcc.log_error("Wrong format of 'transaction_hash', got: {}".format(
                    erc20_deposit_object["transaction_hash"]))
            else:
                lcc.log_info("'transaction_hash' has correct format: hex")
            if not base_test.type_validator.is_account_id(erc20_deposit_object["account"]):
                lcc.log_error("Wrong format of 'account', got {}".format(erc20_deposit_object["account"]))
            else:
                lcc.log_info("'account' has correct format: account_id_type")

            check_that_in(
                erc20_deposit_object,
                "erc20_addr", is_str(),
                "value", is_str(),
                "is_approved", is_bool(),
                "is_sent", is_bool(),
                "approves", is_list(),
                "echo_block_number", is_integer(),
                "extensions", is_list(),
                quiet=True
            )

    def validate_erc20_withdraw_object(self, base_test, erc20_withdraw_object):
        if check_that(
                "'erc20 withdrawal'",
                erc20_withdraw_object, has_length(12),
                quiet=True
        ):
            if not base_test.type_validator.is_withdraw_erc20_id(erc20_withdraw_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(erc20_withdraw_object["id"]))
            else:
                lcc.log_info("'id' has correct format: withdraw_erc20_token_object")
            if not base_test.type_validator.is_eth_address(erc20_withdraw_object["to"]):
                lcc.log_error("Wrong format of 'to', got: {}".format(erc20_withdraw_object["to"]))
            else:
                lcc.log_info("'to' has correct format: ethereum_address_type")
            if not base_test.type_validator.is_erc20_object_id(erc20_withdraw_object["erc20_token"]):
                lcc.log_error("Wrong format of 'erc20_token', got: {}".format(
                    erc20_withdraw_object["erc20_token"]))
            else:
                lcc.log_info("'erc20_token' has correct format: erc20_token_object")
            if not base_test.type_validator.is_account_id(erc20_withdraw_object["account"]):
                lcc.log_error("Wrong format of 'account', got {}".format(erc20_withdraw_object["account"]))
            else:
                lcc.log_info("'account' has correct format: account_id_type")
            # todo: uncomment when will be fix bug ECHO-2088
            # if not base_test.type_validator.is_eth_hash(erc20_withdraw_object["transaction_hash"]):
            #     lcc.log_error("Wrong format of 'transaction_hash', got: {}".format(erc20_withdraw_object["transaction_hash"]))
            # else:
            #     lcc.log_info("'to' has correct format: transaction_hash")

            check_that_in(
                erc20_withdraw_object,
                "withdraw_id", greater_than_or_equal_to(0),
                "value", is_str(),
                "is_approved", is_bool(),
                "is_sent", is_bool(),
                "approves", is_list(),
                "echo_block_number", is_integer(),
                "extensions", is_list(),
                quiet=True
            )

    def validate_global_properties_object(self, base_test, global_properties_object):

        def validate_sidechain_config(base_test, sidechain_config, eth_params, eth_methods):
            if check_that(
                    "sidechain config",
                    sidechain_config, has_length(24),
                    quiet=True
            ):
                for eth_param in eth_params:
                    if not base_test.type_validator.is_hex(sidechain_config[eth_param]):
                        lcc.log_error(
                            "Wrong format of '{}', got: {}".format(eth_param, sidechain_config[eth_param]))
                    else:
                        lcc.log_info("'{}' has correct format: hex".format(eth_param))
                for eth_method in eth_methods:
                    if check_that(
                            "eth_method",
                            sidechain_config[eth_method], has_length(2),
                            quiet=True
                    ):
                        if not base_test.type_validator.is_hex(sidechain_config[eth_method]["method"]):
                            lcc.log_error(
                                "Wrong format of '{}', got: {}".format(eth_method, sidechain_config[eth_method]))
                        else:
                            lcc.log_info("'{}' has correct format: hex".format(eth_method))
                        check_that_in(
                            sidechain_config[eth_method],
                            "gas", is_integer(),
                            quiet=True
                        )
                if not base_test.type_validator.is_eth_asset_id(sidechain_config["ETH_asset_id"]):
                    lcc.log_error("Wrong format of 'ETH_asset_id', got: {}".format(
                        sidechain_config["ETH_asset_id"]))
                else:
                    lcc.log_info("'ETH_asset_id' has correct format: eth_asset_id")
                if not base_test.type_validator.is_btc_asset_id(sidechain_config["BTC_asset_id"]):
                    lcc.log_error("Wrong format of 'BTC_asset_id', got: {}".format(
                        sidechain_config["BTC_asset_id"]))
                else:
                    lcc.log_info("'BTC_asset_id' has correct format: btc_asset_id")
                if check_that(
                        "fines",
                        sidechain_config["fines"], has_length(1),
                        quiet=True
                ):
                    check_that_in(
                        sidechain_config["fines"], "create_eth_address", is_integer(), quiet=True
                    )
                check_that_in(
                    sidechain_config,
                    "satoshis_per_byte", is_integer(),
                    "coefficient_waiting_blocks", is_integer(),
                    "btc_deposit_withdrawal_min", is_integer(),
                    "btc_deposit_withdrawal_fee", is_integer(),
                    "eth_withdrawal_fee", is_integer(),
                    "eth_withdrawal_min", is_integer(),
                    quiet=True
                )
                base_test.check_uint64_numbers(
                    sidechain_config,
                    "gas_price",
                    quiet=True
                )
                if check_that(
                        "eth_update_contract_address",
                        sidechain_config["eth_update_contract_address"], has_length(2),
                        quiet=True
                ):
                    check_that_in(
                        sidechain_config["eth_update_contract_address"], "method", is_str(), quiet=True
                    )
                    check_that_in(
                        sidechain_config["eth_update_contract_address"], "gas", is_integer(), quiet=True
                    )

        def validate_erc20_config(base_test, erc20_config, erc20_methods):
            if check_that(
                    "erc20 config",
                    erc20_config, has_length(6),
                    quiet=True
            ):
                if not base_test.type_validator.is_hex(erc20_config["contract_code"]):
                    lcc.log_error("Wrong format of 'contract_code', got: {}".format(
                        erc20_config["contract_code"]))
                else:
                    lcc.log_info("'contract_code' has correct format: hex")
                if not base_test.type_validator.is_hex(erc20_config["transfer_topic"]):
                    lcc.log_error("Wrong format of 'transfer_topic', got: {}".format(
                        erc20_config["transfer_topic"]))
                else:
                    lcc.log_info("'transfer_topic' has correct format: hex")
                check_that_in(
                    erc20_config,
                    "create_token_fee", is_integer(),
                    quiet=True
                )
                for erc20_method in erc20_methods:
                    if check_that(
                            "erc20_method",
                            erc20_config[erc20_method], has_length(2),
                            quiet=True
                    ):
                        if not base_test.type_validator.is_hex(erc20_config[erc20_method]["method"]):
                            lcc.log_error("Wrong format of '{}', got: {}".format(
                                erc20_method, erc20_config[erc20_method]))
                        else:
                            lcc.log_info("'{}' has correct format: hex".format(erc20_method))
                        check_that_in(
                            erc20_config[erc20_method],
                            "gas", is_integer(),
                            quiet=True
                        )

        def no_fee(actual_fee):
            check_that(
                "fee",
                actual_fee, has_length(0),
                quiet=True
            )

        def only_fee(actual_fee):
            if check_that(
                    "fee",
                    actual_fee, has_length(1),
                    quiet=True
            ):
                check_that_in(
                    actual_fee,
                    "fee", is_integer(),
                    quiet=True
                )

        def fee_with_price_per_kbyte(actual_fee):
            if check_that(
                    "fee",
                    actual_fee, has_length(2),
                    quiet=True
            ):
                check_that_in(
                    actual_fee,
                    "fee", is_integer(),
                    "price_per_kbyte", is_integer(),
                    quiet=True
                )

        def account_create_fee(actual_fee):
            if check_that(
                    "fee",
                    actual_fee, has_length(3),
                    quiet=True
            ):
                check_that_in(
                    actual_fee,
                    "basic_fee", is_integer(),
                    "premium_fee", is_integer(),
                    "price_per_kbyte", is_integer(),
                    quiet=True
                )

        def asset_create_fee(actual_fee):
            if check_that(
                    "fee",
                    actual_fee, has_length(4),
                    quiet=True
            ):
                check_that_in(
                    actual_fee,
                    "symbol3", is_integer(),
                    "symbol4", is_integer(),
                    "long_symbol", is_integer(),
                    "price_per_kbyte", is_integer(),
                    quiet=True
                )

        def pool_fee(actual_fee):
            if check_that(
                    "fee",
                    actual_fee, has_length(2),
                    quiet=True
            ):
                check_that_in(
                    actual_fee,
                    "fee", is_integer(),
                    "pool_fee", is_integer(),
                    quiet=True
                )

        def check_default_fee_for_operation(base_test, current_fees, operations, check_kind):
            for operation in operations:
                for fee in current_fees:
                    if fee[0] == base_test.all_operations.get(operation.upper()):
                        lcc.log_info("Check default fee for '{}' operation, "
                                     "operation_id is '{}'".format(operation, fee[0]))
                        check_kind(fee[1])
                        break

        def show_wrong_fee_operations(base_test, current_operations_ids, operations_for_checking):
            all_operations_names = [key for key in base_test.all_operations.keys()]
            all_operations_ids = [value for value in base_test.all_operations.values()]
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

        fee_with_price_per_kbyte_operations = ["account_update", "asset_update", "proposal_create",
                                               "proposal_update", "account_address_create"]
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
                               'committee_member_activate', 'committee_member_deactivate',
                               'committee_frozen_balance_deposit', 'committee_frozen_balance_withdraw',
                               'sidechain_eth_approve_address', 'sidechain_issue', 'sidechain_burn',
                               'sidechain_erc20_issue', 'sidechain_erc20_burn', 'sidechain_btc_create_address',
                               'sidechain_btc_create_intermediate_deposit', 'sidechain_btc_intermediate_deposit',
                               'sidechain_btc_deposit', 'sidechain_btc_withdraw', 'sidechain_btc_approve_withdraw',
                               'sidechain_btc_aggregate', 'sidechain_erc20_approve_token_withdraw',
                               'sidechain_eth_send_deposit', 'sidechain_eth_send_withdraw',
                               'sidechain_eth_update_contract_address',
                               'sidechain_erc20_send_deposit_token', 'sidechain_erc20_send_withdraw_token']
        no_fee_operations = ["balance_claim", "balance_unfreeze", 'contract_internal_create',
                             'contract_internal_call', 'contract_selfdestruct', 'evm_address_register_operation']
        account_create_fee_operations = ["account_create"]
        asset_create_fee_operations = ["asset_create"]
        pool_fee_operations = ["sidechain_erc20_register_token"]

        if check_that(
                "global properties",
                global_properties_object, has_length(3),
                quiet=True
        ):
            if not base_test.type_validator.is_global_object_id(global_properties_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(global_properties_object["id"]))
            else:
                lcc.log_info("'id' has correct format: global_property_object_type")
            check_that_in(
                global_properties_object,
                "parameters", is_dict(),
                "active_committee_members", is_list(),
                quiet=True
            )

        lcc.set_step("Check global parameters: 'current_fees' field")
        parameters = global_properties_object["parameters"]
        if check_that(
                "parameters",
                parameters, has_length(25),
                quiet=True
        ):
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
                "maximum_authority_membership", is_integer(),
                "max_authority_depth", is_integer(),
                "block_producer_reward_ratio", is_integer(),
                "block_emission_amount", is_integer(),
                "frozen_balances_multipliers", is_list(),
                "committee_maintenance_intervals_to_deposit", is_integer(),
                "committee_balance_unfreeze_duration_seconds", is_integer(),
                "echorand_config", is_dict(),
                "sidechain_config", is_dict(),
                "erc20_config", is_dict(),
                "gas_price", is_dict(),
                "extensions", is_list(),
                quiet=True
            )
            check_that(
                "committee_frozen_balance_to_activate",
                parameters["committee_frozen_balance_to_activate"], is_integer(),
                quiet=True
            )

            lcc.set_step("Check global parameters: 'current_fees' field")
            current_fees = parameters["current_fees"]
            if check_that(
                    "current fees",
                    current_fees, has_length(2),
                    quiet=True
            ):
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
                    check_that(
                        "frozen_balance",
                        balance, is_integer(),
                        quiet=True
                    )

            lcc.set_step("Check the count of fees for operations")
            fee_parameters = current_fees["parameters"]
            require_that(
                "count of fees for operations",
                fee_parameters, has_length(65)
            )

            lcc.set_step("Check that count of checking fees fields equal to all operations")
            checking_operations_fee_types = [fee_with_price_per_kbyte_operations, only_fee_operations,
                                             no_fee_operations,
                                             account_create_fee_operations, asset_create_fee_operations,
                                             pool_fee_operations]
            all_checking_operations = []
            for fee_type in checking_operations_fee_types:
                all_checking_operations.extend(fee_type)
            check_that("'length of checking fees fields equal to all operations'", all_checking_operations,
                       has_length(65))

        fee_with_price_per_kbyte_operations_ids, only_fee_operations_ids, no_fee_operations_ids, \
        account_create_fee_operations_ids, asset_create_fee_operations_ids, \
        pool_fee_operations_ids = [], [], [], [], [], []

        lcc.set_step("Save the number of types of current_fees")
        fee_parameters = current_fees["parameters"]
        for fee_parameter in fee_parameters:
            parameter = fee_parameter[1]
            if len(parameter) == 0:
                no_fee_operations_ids.append(fee_parameter[0])
                base_test.no_fee_count += 1
                continue
            if len(parameter) == 1 and "fee" in parameter:
                base_test.only_fee_count += 1
                only_fee_operations_ids.append(fee_parameter[0])
                continue
            if len(parameter) == 2 and ("fee" and "price_per_kbyte") in parameter:
                fee_with_price_per_kbyte_operations_ids.append(fee_parameter[0])
                base_test.fee_with_price_per_kbyte_count += 1
                continue
            if len(parameter) == 2 and ("membership_annual_fee" and "membership_lifetime_fee") in parameter:
                only_fee_operations_ids.append(fee_parameter[0])
                base_test.account_update_fee_count += 1
                continue
            if len(parameter) == 2 and ("fee" and "pool_fee") in parameter:
                account_create_fee_operations_ids.append(fee_parameter[0])
                base_test.pool_fee_count += 1
                continue
            if len(parameter) == 3 and ("basic_fee" and "premium_fee" and "price_per_kbyte") in parameter:
                account_create_fee_operations_ids.append(fee_parameter[0])
                base_test.account_create_fee_count += 1
                continue
            if len(parameter) == 4 and (
                    "symbol3" and "symbol4" and "long_symbol" and "price_per_kbyte") in parameter:
                asset_create_fee_operations_ids.append(fee_parameter[0])
                base_test.asset_create_count += 1
                continue
            else:
                lcc.log_warning("Warn: Added new option for calculating fee for the operation, got: '{}'".format(
                    fee_parameter))

        lcc.set_step("Check 'fee_with_price_per_kbyte' for operations")
        check_that(
            "'fee_with_price_per_kbyte' operation count",
            fee_with_price_per_kbyte_operations, has_length(base_test.fee_with_price_per_kbyte_count),
            quiet=True
        )
        check_default_fee_for_operation(
            base_test,
            fee_parameters,
            fee_with_price_per_kbyte_operations,
            fee_with_price_per_kbyte
        )
        show_wrong_fee_operations(
            base_test,
            fee_with_price_per_kbyte_operations_ids,
            fee_with_price_per_kbyte_operations
        )

        lcc.set_step("Check 'only_fee' for operations")
        check_that(
            "'only_fee' operation count",
            only_fee_operations, has_length(base_test.only_fee_count),
            quiet=True
        )
        check_default_fee_for_operation(
            base_test,
            fee_parameters,
            only_fee_operations,
            only_fee
        )
        show_wrong_fee_operations(
            base_test,
            only_fee_operations_ids,
            only_fee_operations
        )

        lcc.set_step("Check 'no_fee' for operations")
        check_that(
            "'no_fee' operation count",
            no_fee_operations, has_length(base_test.no_fee_count),
            quiet=True
        )
        check_default_fee_for_operation(
            base_test,
            fee_parameters,
            no_fee_operations,
            no_fee
        )
        show_wrong_fee_operations(
            base_test,
            no_fee_operations_ids,
            no_fee_operations
        )

        lcc.set_step("Check 'account_create_fee' for operations")
        check_that(
            "'account_create_fee' operation count",
            account_create_fee_operations, has_length(base_test.account_create_fee_count),
            quiet=True
        )
        check_default_fee_for_operation(
            base_test,
            fee_parameters,
            account_create_fee_operations,
            account_create_fee
        )
        show_wrong_fee_operations(
            base_test,
            account_create_fee_operations_ids,
            account_create_fee_operations
        )

        lcc.set_step("Check 'asset_create_fee' for operations")
        check_that(
            "'asset_create_fee' operation count",
            asset_create_fee_operations, has_length(base_test.asset_create_count),
            quiet=True
        )
        check_default_fee_for_operation(
            base_test,
            fee_parameters,
            asset_create_fee_operations,
            asset_create_fee
        )
        show_wrong_fee_operations(
            base_test,
            asset_create_fee_operations_ids,
            asset_create_fee_operations
        )

        lcc.set_step("Check 'pool_fee' for operations")
        check_that(
            "'pool_fee' operation count",
            pool_fee_operations, has_length(base_test.pool_fee_count),
            quiet=True
        )
        if not check_default_fee_for_operation(
                base_test,
                fee_parameters,
                pool_fee_operations,
                pool_fee
        ):
            show_wrong_fee_operations(
                base_test,
                pool_fee_operations_ids,
                pool_fee_operations
            )

        lcc.set_step("Check global parameters: 'echorand_config' field")
        echorand_config = parameters["echorand_config"]
        if check_that(
                "echorand_config",
                echorand_config, has_length(9),
                quiet=True
        ):
            check_that_in(
                echorand_config,
                "_time_generate", is_integer(),
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
        validate_sidechain_config(base_test, sidechain_config, eth_params, eth_methods)

        lcc.set_step("Check global parameters: 'erc20_config' field")
        erc20_config = parameters["erc20_config"]
        erc20_methods = ["check_balance_method", "burn_method", "issue_method"]
        validate_erc20_config(base_test, erc20_config, erc20_methods)

        lcc.set_step("Check global parameters: 'gas_price' field")
        gas_price = parameters["gas_price"]
        if check_that(
                "gas price",
                gas_price, has_length(2),
                quiet=True
        ):
            check_that_in(
                gas_price,
                "price", is_integer(),
                "gas_amount", is_integer(),
                quiet=True
            )

    def validate_dynamic_global_property_object(self, base_test, dynamic_global_property_object):
        dynamic_global_properties = ["head_block_number", "committee_budget",
                                     "dynamic_flags", "last_irreversible_block_num"]
        dynamic_global_properties_time = ["time", "next_maintenance_time", "last_budget_time"]
        if check_that(
                "dynamic global properties",
                dynamic_global_property_object, has_length(10),
                quiet=True
        ):
            if not base_test.type_validator.is_dynamic_global_object_id(dynamic_global_property_object["id"]):
                lcc.log_error("Wrong format of 'dynamic_global_object_id', got: {}".format(
                    dynamic_global_property_object))
            else:
                lcc.log_info("'id' has correct format: dynamic_global_object_id")
            for property_ in dynamic_global_properties:
                base_test.check_uint64_numbers(
                    dynamic_global_property_object,
                    property_,
                    quiet=True
                )
                value = int(dynamic_global_property_object[property_])
                check_that(
                    property_,
                    value, greater_than_or_equal_to(0),
                    quiet=True
                )
            if not base_test.type_validator.is_hex(dynamic_global_property_object["head_block_id"]):
                lcc.log_error("Wrong format of 'head_block_id', got: {}".format(dynamic_global_property_object))
            else:
                lcc.log_info("'head_block_id' has correct format: hex")

            for time_property in dynamic_global_properties_time:
                if not base_test.type_validator.is_iso8601(dynamic_global_property_object[time_property]):
                    lcc.log_error(
                        "Wrong format of '{}', got: {}".format(
                            time_property,
                            dynamic_global_property_object[time_property]
                        )
                    )
                else:
                    lcc.log_info("'{}' has correct format: iso8601".format(time_property))
            check_that_in(
                dynamic_global_property_object,
                "extensions", is_list(),
                quiet=True
            )

    def validate_chain_properties_object(self, base_test, chain_properties_object):
        if check_that(
                "chain properties",
                chain_properties_object, has_length(3),
                quiet=True
        ):
            if not base_test.type_validator.is_chain_property_object_id(chain_properties_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(chain_properties_object["id"]))
            else:
                lcc.log_info("'id' has correct format: chain_property_object_type")
            if not base_test.type_validator.is_hex(chain_properties_object["chain_id"]):
                lcc.log_error("Wrong format of 'chain_id', got: {}".format(chain_properties_object["chain_id"]))
            else:
                lcc.log_info("'chain_id' has correct format: hex")
            check_that_in(
                chain_properties_object,
                "extensions", is_list(),
                quiet=True
            )

    def validate_asset_dynamic_data_object(self, base_test, asset_dynamic_data_object):
        if check_that(
                "asset dynamic data",
                asset_dynamic_data_object, has_length(5),
                quiet=True
        ):
            if not base_test.type_validator.is_dynamic_asset_data_id(asset_dynamic_data_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(asset_dynamic_data_object["id"]))
            else:
                lcc.log_info("'id' has correct formt: dynamic_asset_data_object_type")

            check_that_in(
                asset_dynamic_data_object,
                "current_supply", is_str(),
                "accumulated_fees", is_integer(),
                "fee_pool", is_integer(),
                "extensions", is_list(),
                quiet=True
            )

    def validate_asset_bitasset_data_object(self, base_test, asset_bitasset_data_object):

        def validate_price_object(base_test, price_object):
            check_that_in(
                price_object,
                "base", is_dict(),
                "quote", is_dict(),
                quiet=True
            )
            for key in price_object:
                price_part = price_object[key]
                base_test.check_uint64_numbers(
                    price_part,
                    "amount",
                    quiet=True
                )
                if not base_test.type_validator.is_asset_id(price_part["asset_id"]):
                    lcc.log_error("Wrong format of {} 'asset_id', got: {}".format(
                        key, price_part["asset_id"]))
                else:
                    lcc.log_info("{} 'asset_id' has correct format: asset_id".format(key))

        if check_that(
                "asset bitasset data",
                asset_bitasset_data_object, has_length(6),
                quiet=True
        ):
            if not base_test.type_validator.is_bitasset_id(asset_bitasset_data_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(asset_bitasset_data_object["id"]))
            else:
                lcc.log_info("'id' has correct format: bitasset_data_object_type")
            if not base_test.type_validator.is_iso8601(
                    asset_bitasset_data_object["current_feed_publication_time"]):
                lcc.log_error("Wrong format of 'current_feed_publication_time', got: {}".format(
                    asset_bitasset_data_object["current_feed_publication_time"]))
            else:
                lcc.log_info("'current_feed_publication_time' has correct format: iso8601")

            if check_that_in(
                    asset_bitasset_data_object,
                    "feeds", is_list(),
                    "options", is_dict(),
                    "extensions", is_list(),
                    quiet=True
            ):
                options = asset_bitasset_data_object["options"]
                if check_that(
                        "options",
                        options, has_length(4),
                        quiet=True
                ):
                    if not base_test.type_validator.is_asset_id(options["short_backing_asset"]):
                        lcc.log_error("Wrong format of 'short_backing_asset', got: {}".format(
                            options["short_backing_asset"]))
                    else:
                        lcc.log_info("'short_backing_asset' has correct format: asset_id")
                    check_that_in(
                        options,
                        "feed_lifetime_sec", is_integer(),
                        "minimum_feeds", is_integer(),
                        "extensions", is_list(),
                        quiet=True
                    )

    def validate_account_balance_object(self, base_test, account_balance_object):
        if check_that(
                "account balance object",
                account_balance_object, has_length(5),
                quiet=True
        ):
            if not base_test.type_validator.is_account_balance_id(account_balance_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(account_balance_object["id"]))
            else:
                lcc.log_info("'id' has correct format: account_balance_id")
            if not base_test.type_validator.is_account_id(account_balance_object["owner"]):
                lcc.log_error("Wrong format of 'owner', got: {}".format(account_balance_object["owner"]))
            else:
                lcc.log_info("'owner' has correct format: account_id")
            if not base_test.type_validator.is_asset_id(account_balance_object["asset_type"]):
                lcc.log_error("Wrong format of 'asset_type', got: {}".format(account_balance_object["asset_type"]))
            else:
                lcc.log_info("'asset_type' has correct format: asset_id")

            check_that_in(
                account_balance_object,
                "balance", is_integer(),
                "extensions", is_list(),
                quiet=True
            )

    def validate_account_statistics_object(self, base_test, account_statistics_object):
        if check_that(
                "account statistics object",
                account_statistics_object, has_length(10),
                quiet=True
        ):
            if not base_test.type_validator.is_account_statistics_id(account_statistics_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(account_statistics_object["id"]))
            else:
                lcc.log_info("'id' has correct format: account_statistics_id")
            if not base_test.type_validator.is_account_id(account_statistics_object["owner"]):
                lcc.log_error("Wrong format of 'owner', got: {}".format(account_statistics_object["owner"]))
            else:
                lcc.log_info("'owner' has correct format: account_id")
            if not base_test.type_validator.is_account_transaction_history_id(
                    account_statistics_object["most_recent_op"]):
                lcc.log_error("Wrong format of 'most_recent_op', got: {}".format(
                    account_statistics_object["most_recent_op"]))
            else:
                lcc.log_info("'most_recent_op' has correct format: account_transaction_history_id")
            check_that_in(
                account_statistics_object,
                "total_ops", is_integer(),
                "removed_ops", is_integer(),
                "total_blocks", is_integer(),
                "total_core_in_orders", is_integer(),
                "created_eth_address", is_bool(),
                "committeeman_rating", is_integer(),
                "extensions", is_list(),
                quiet=True
            )

    def validate_block_summary_object(self, base_test, block_summary_object):
        if check_that(
                "block summary object",
                block_summary_object, has_length(3),
                quiet=True
        ):
            if not base_test.type_validator.is_block_summary_id(block_summary_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(block_summary_object["id"]))
            else:
                lcc.log_info("'id' has correct format: block_summary_id")
            if not base_test.type_validator.is_bytes(block_summary_object["block_id"], 20):
                lcc.log_error("Wrong format of 'block_id', got: {}".format(block_summary_object["block_id"]))
            else:
                lcc.log_info("'block_id' has correct format: bytes")
            check_that_in(
                block_summary_object,
                "extensions", is_list(),
                quiet=True
            )

    def validate_account_address_object(self, base_test, account_address_object):
        if check_that(
                "account addresses object",
                account_address_object, has_length(5),
                quiet=True
        ):
            if not base_test.type_validator.is_account_address_id(account_address_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(account_address_object["id"]))
            else:
                lcc.log_info("'id' has correct format: account_address_object_type")
            if not base_test.type_validator.is_account_id(account_address_object["owner"]):
                lcc.log_error("Wrong format of 'owner', got: {}".format(account_address_object["owner"]))
            else:
                lcc.log_info("'owner' has correct format: account_object_type")
            if not base_test.type_validator.is_hex(account_address_object["address"]):
                lcc.log_error("Wrong format of 'address', got: {}".format(account_address_object["owner"]))
            else:
                lcc.log_info("'address' has correct format: hex")
            check_that_in(
                account_address_object,
                "label", is_str(),
                "extensions", is_list(),
                quiet=True
            )

    def validate_contract_balance_object(self, base_test, contract_balance_object):
        if check_that(
                "contract balance object",
                contract_balance_object, has_length(5),
                quiet=True
        ):
            if not base_test.type_validator.is_contract_balance_object_id(contract_balance_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(contract_balance_object["id"]))
            else:
                lcc.log_info("'id' has correct format: contract_balance_object_type")
            if not base_test.type_validator.is_contract_id(contract_balance_object["owner"]):
                lcc.log_error("Wrong format of 'owner', got: {}".format(contract_balance_object["owner"]))
            else:
                lcc.log_info("'owner' has correct format: contract_object_type")
            if not base_test.type_validator.is_asset_id(contract_balance_object["asset_type"]):
                lcc.log_error("Wrong format of 'asset_type', got: {}".format(
                    contract_balance_object["asset_type"]))
            else:
                lcc.log_info("'asset_type' has correct format: asset_id")
            check_that_in(
                contract_balance_object,
                "balance", is_integer(),
                "extensions", is_list(),
                quiet=True
            )

    def validate_contract_history_object(self, base_test, contract_history_object):
        if len(contract_history_object) == 7:
            if not base_test.type_validator.is_operation_history_id(contract_history_object["parent_op_id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(contract_history_object["parent_op_id"]))
            else:
                lcc.log_info("'id' has correct format: parent_op_id")
        else:
            if check_that(
                    "contract history object",
                    contract_history_object, has_length(6), quiet=True):
                if not base_test.type_validator.is_contract_history_id(contract_history_object["id"]):
                    lcc.log_error("Wrong format of 'id', got: {}".format(contract_history_object["id"]))
                else:
                    lcc.log_info("'id' has correct format: contract_history_id")
                if not base_test.type_validator.is_contract_id(contract_history_object["contract"]):
                    lcc.log_error("Wrong format of 'contract', got: {}".format(contract_history_object["contract"]))
                else:
                    lcc.log_info("'contract' has correct format: contract_id")
                if not base_test.type_validator.is_operation_history_id(contract_history_object["operation_id"]):
                    lcc.log_error("Wrong format of 'operation_id', got: {}".format(
                        contract_history_object["operation_id"]))
                else:
                    lcc.log_info("'operation_id' has correct format: operation_history_id")
                if not base_test.type_validator.is_contract_history_id(contract_history_object["next"]):
                    lcc.log_error("Wrong format of 'next', got: {}".format(contract_history_object["next"]))
                else:
                    lcc.log_info("'next' has correct format: contract_history_id")
                check_that_in(
                    contract_history_object,
                    "sequence", is_integer(),
                    "extensions", is_list(),
                    quiet=True
                )

    def validate_contract_statistics_object(self, base_test, contract_statistics_object):
        if check_that(
                "contract statistics object",
                contract_statistics_object, has_length(6),
                quiet=True
        ):
            if not base_test.type_validator.is_contract_statistics_id(contract_statistics_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(contract_statistics_object["id"]))
            else:
                lcc.log_info("'id' has correct format: contract_statistics_id")
            if not base_test.type_validator.is_contract_id(contract_statistics_object["owner"]):
                lcc.log_error("Wrong format of 'owner', got: {}".format(contract_statistics_object["owner"]))
            else:
                lcc.log_info("'owner' has correct format: contract_object_type")
            if not base_test.type_validator.is_contract_history_id(contract_statistics_object["most_recent_op"]):
                lcc.log_error("Wrong format of 'most_recent_op', got: {}".format(
                    contract_statistics_object["most_recent_op"]))
            else:
                lcc.log_info("'most_recent_op' has correct format: contract_history_id")
            check_that_in(
                contract_statistics_object,
                "total_ops", is_integer(),
                "removed_ops", is_integer(),
                "extensions", is_list(),
                quiet=True
            )

    def validate_ethrpc_transaction(self, transaction):
        if require_that("transactions", transaction, has_length(14)):
            if not self.type_validator.is_SHA3_256(transaction["blockHash"]):
                lcc.log_error("Wrong format of 'blockHash', got: '{}'".format(transaction["blockHash"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            if not self.type_validator.is_eth_hash(transaction["blockNumber"]):
                lcc.log_error("Wrong format of 'blockNumber', got: '{}'".format(transaction["blockNumber"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            if not self.type_validator.is_eth_hash(transaction["gas"]):
                lcc.log_error("Wrong format of 'gas', got: '{}'".format(transaction["gas"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            if not self.type_validator.is_eth_hash(transaction["gasPrice"]):
                lcc.log_error("Wrong format of 'gasPrice', got: '{}'".format(transaction["gasPrice"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            if not self.type_validator.is_SHA3_256(transaction["hash"]):
                lcc.log_error("Wrong format of 'hash', got: '{}'".format(transaction["hash"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            if not self.type_validator.is_eth_hash(transaction["nonce"]):
                lcc.log_error("Wrong format of 'nonce', got: '{}'".format(transaction["nonce"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            if not self.type_validator.is_eth_hash(transaction["to"]):
                lcc.log_error("Wrong format of 'to', got: '{}'".format(transaction["to"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            if not self.type_validator.is_eth_hash(transaction["transactionIndex"]):
                lcc.log_error(
                    "Wrong format of 'transactionIndex', got: '{}'".format(transaction["transactionIndex"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            check_that("input", transaction["input"], equal_to(""))
            check_that("value", transaction["value"], equal_to("0x01"))
            if not self.type_validator.is_eth_hash(transaction["v"]):
                lcc.log_error(
                    "Wrong format of 'v', got: '{}'".format(transaction["v"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            if not self.type_validator.is_eth_hash(transaction["r"]):
                lcc.log_error(
                    "Wrong format of 'r', got: '{}'".format(transaction["r"]))
            else:
                lcc.log_info("'r' has correct format: eth_hash")
            if not self.type_validator.is_eth_hash(transaction["s"]):
                lcc.log_error(
                    "Wrong format of 's', got: '{}'".format(transaction["s"]))
            else:
                lcc.log_info("'s' has correct format: eth_hash")

    def validate_ethrpc_block(self, result):
        if require_that("'result'", result, has_length(19)):
            if not self.type_validator.is_eth_hash(result["number"]):
                lcc.log_error("Wrong format of 'number', got: '{}'".format(result["number"]))
            else:
                lcc.log_info("'result' has correct format: number")
            if not self.type_validator.is_eth_hash(result["hash"]):
                lcc.log_error("Wrong format of 'hash', got: '{}'".format(result["hash"]))
            else:
                lcc.log_info("'result' has correct format: hash")
            if not self.type_validator.is_eth_hash(result["parentHash"]):
                lcc.log_error("Wrong format of 'parentHash', got: '{}'".format(result["parentHash"]))
            else:
                lcc.log_info("'result' has correct format: parentHash")
            if not self.type_validator.is_eth_hash(result["nonce"]):
                lcc.log_error("Wrong format of 'nonce', got: '{}'".format(result["nonce"]))
            else:
                lcc.log_info("'result' has correct format: nonce")
            if not self.type_validator.is_eth_hash(result["sha3Uncles"]):
                lcc.log_error("Wrong format of 'sha3Uncles', got: '{}'".format(result["sha3Uncles"]))
            else:
                lcc.log_info("'result' has correct format: sha3Uncles")
            if not self.type_validator.is_eth_hash(result["logsBloom"]):
                lcc.log_error("Wrong format of 'logsBloom', got: '{}'".format(result["logsBloom"]))
            else:
                lcc.log_info("'result' has correct format: logsBloom")
            if not self.type_validator.is_eth_hash(result["transactionsRoot"]):
                lcc.log_error("Wrong format of 'transactionsRoot', got: '{}'".format(result["transactionsRoot"]))
            else:
                lcc.log_info("'result' has correct format: transactionsRoot")
            if not self.type_validator.is_eth_hash(result["stateRoot"]):
                lcc.log_error("Wrong format of 'stateRoot', got: '{}'".format(result["stateRoot"]))
            else:
                lcc.log_info("'result' has correct format: stateRoot")
            if not self.type_validator.is_eth_hash(result["receiptsRoot"]):
                lcc.log_error("Wrong format of 'receiptsRoot', got: '{}'".format(result["receiptsRoot"]))
            else:
                lcc.log_info("'result' has correct format: receiptsRoot")
            if not self.type_validator.is_eth_hash(result["miner"]):
                lcc.log_error("Wrong format of 'receiptsRoot', got: '{}'".format(result["miner"]))
            else:
                lcc.log_info("'result' has correct format: miner")
            if not self.type_validator.is_eth_hash(result["difficulty"]):
                lcc.log_error("Wrong format of 'difficulty', got: '{}'".format(result["difficulty"]))
            else:
                lcc.log_info("'result' has correct format: difficulty")
            if not self.type_validator.is_eth_hash(result["totalDifficulty"]):
                lcc.log_error("Wrong format of 'totalDifficulty', got: '{}'".format(result["totalDifficulty"]))
            else:
                lcc.log_info("'result' has correct format: totalDifficulty")
            if not self.type_validator.is_eth_hash(result["extraData"]):
                lcc.log_error("Wrong format of 'extraData', got: '{}'".format(result["extraData"]))
            else:
                lcc.log_info("'result' has correct format: extraData")
            if not self.type_validator.is_eth_hash(result["size"]):
                lcc.log_error("Wrong format of 'size', got: '{}'".format(result["size"]))
            else:
                lcc.log_info("'result' has correct format: size")
            if not self.type_validator.is_eth_hash(result["gasLimit"]):
                lcc.log_error("Wrong format of 'gasLimit', got: '{}'".format(result["gasLimit"]))
            else:
                lcc.log_info("'result' has correct format: gasLimit")
            if not self.type_validator.is_eth_hash(result["gasUsed"]):
                lcc.log_error("Wrong format of 'gasUsed', got: '{}'".format(result["gasUsed"]))
            else:
                lcc.log_info("'result' has correct format: gasUsed")
            if not self.type_validator.is_eth_hash(result["timestamp"]):
                lcc.log_error("Wrong format of 'timestamp', got: '{}'".format(result["timestamp"]))
            else:
                lcc.log_info("'result' has correct format: timestamp")
            check_that("uncles", result["uncles"], is_list())
            if check_that("transactions", result["transactions"], is_list()):
                if len(result["transactions"]) > 0:
                    for transaction in result["transactions"]:
                        self.validate_ethrpc_transaction(transaction)

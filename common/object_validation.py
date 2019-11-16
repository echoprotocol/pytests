# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import has_length, is_integer, check_that_in, check_that, is_dict, is_list,\
    require_that, is_str, is_


class ObjectValidator(object):

    @staticmethod
    def validate_account_object(base_test, account_info):

        if check_that("account_info", account_info, has_length(16)):
            check_that_in(
                account_info,
                "id", is_str(),
                "network_fee_percentage", is_integer(),
                "active", is_dict(),
                "options", is_dict(),
                "whitelisting_accounts", is_list(),
                "whitelisting_accounts", is_list(),
                "blacklisting_accounts", is_list(),
                "whitelisted_accounts", is_list(),
                "blacklisted_accounts", is_list(),
                "active_special_authority", is_list(),
                "top_n_control_flags", is_integer(),
                "accumulated_reward", is_integer(),
                "extensions", is_list(),
                quiet=True
            )
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
            if len(account_info) == 21:
                if not base_test.type_validator.is_vesting_balance_id(account_info["cashback_vb"]):
                    lcc.log_error("Wrong format of 'cashback_vb', got: {}".format(account_info["cashback_vb"]))
                else:
                    lcc.log_info("'cashback_vb' has correct format: vesting_balance_object_type")

            lcc.set_step("Check 'active' field")
            if check_that("active", account_info["active"], has_length(3)):
                check_that_in(
                    account_info["active"],
                    "weight_threshold", is_integer(),
                    "account_auths", is_list(),
                    "key_auths", is_list(),
                    quiet=True
                )

            lcc.set_step("Check 'options' field")
            if check_that("options", account_info["options"], has_length(3)):
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

    @staticmethod
    def validate_asset_object(base_test, asset):

        def validate_core_exchange_rate_structure(base_test, core_exchange_rate):
            check_that_in(
                core_exchange_rate,
                "base", is_dict(),
                "quote", is_dict(),
                quiet=True
            )
            for key in core_exchange_rate:
                core_exchange_rate_part = core_exchange_rate[key]
                base_test.check_uint64_numbers(core_exchange_rate_part, "amount", quiet=True)
                if not base_test.type_validator.is_asset_id(core_exchange_rate_part["asset_id"]):
                    lcc.log_error("Wrong format of {} 'asset_id', got: {}".format(
                        key, core_exchange_rate_part["asset_id"]))
                else:
                    lcc.log_info("{} 'asset_id' has correct format: asset_id".format(key))

        require_that(
            "'length of chain asset'",
            asset, has_length(7)
        )

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
        require_that("'options'", options, has_length(8))
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
        require_that(
            "'core_exchange_rate'",
            core_exchange_rate, has_length(2)
        )
        validate_core_exchange_rate_structure(base_test, core_exchange_rate)
        base_test.check_uint64_numbers(options, "max_supply", quiet=True)

    @staticmethod
    def validate_committee_member_object(base_test, committee_member):
        require_that("'committee member'", committee_member, has_length(6))
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

    @staticmethod
    def validate_proposal_object(base_test, proposal_object):
        require_that("'proposal object'", proposal_object, has_length(7), quiet=True)
        if not base_test.type_validator.is_proposal_id(proposal_object["id"]):
            lcc.log_error("Wrong format of 'id', got: {}".format(proposal_object["id"]))
        else:
            lcc.log_info("'id' has correct format: proposal_object_type")
        if not base_test.type_validator.is_iso8601(proposal_object["expiration_time"]):
            lcc.log_error("Wrong format of 'expiration_time', got: {}".format(proposal_object["expiration_time"]))
        else:
            lcc.log_info("'expiration_time' has correct format: iso8601")
        proposed_transaction = proposal_object["proposed_transaction"]
        check_that("'proposed transaction'", proposed_transaction, has_length(5), quiet=True)
        if not base_test.type_validator.is_iso8601(proposed_transaction["expiration"]):
            lcc.log_error("Wrong format of 'expiration', got: {}".format(proposed_transaction["expiration"]))
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

    @staticmethod
    def validate_vesting_balance_object(base_test, vesting_balance_object):
        if check_that("balance_object", vesting_balance_object, has_length(5)):
            if not base_test.type_validator.is_vesting_balance_id(vesting_balance_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(vesting_balance_object["id"]))
            else:
                lcc.log_info("'id' has correct format: vesting_balance_object_type")
            balance = vesting_balance_object["balance"]
            if check_that("balance", balance, has_length(2)):
                base_test.check_uint256_numbers(balance, "amount", quiet=True)
                if not base_test.type_validator.is_asset_id(balance["asset_id"]):
                    lcc.log_error("Wrong format of 'asset_id', got: {}".format(vesting_balance_object["asset_id"]))
                else:
                    lcc.log_info("'asset_id' has correct format: asset_object_type")
            policy = vesting_balance_object["policy"]
            if check_that("policy", policy, has_length(2)):
                first_element = policy[0]
                second_element = policy[1]
                # todo: first_element='0' - come from bitshares. Remove when corrected in Echo
                check_that("first element", first_element, is_(0), quiet=True)
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
                base_test.check_uint256_numbers(second_element, "begin_balance", quiet=True)

    @staticmethod
    def validate_balance_object(base_test, balance_object):
        if check_that("balance_object", balance_object, has_length(5)):
            if not base_test.type_validator.is_balance_id(balance_object["id"]):
                lcc.log_error("Wrong format of 'balance_id', got: {}".format(balance_object["id"]))
            else:
                lcc.log_info("'balance_id' has correct format: balance_id")
            if not base_test.type_validator.is_iso8601(balance_object["last_claim_date"]):
                lcc.log_error(
                    "Wrong format of 'last_claim_date', got: {}".format(balance_object["last_claim_date"]))
            else:
                lcc.log_info("'last_claim_date' has correct format: iso8601")
            base_test.check_uint256_numbers(balance_object["balance"], "amount", quiet=True)
            if not base_test.type_validator.is_asset_id(balance_object["balance"]["asset_id"]):
                lcc.log_error(
                    "Wrong format of 'asset_id', got: {}".format(balance_object["balance"]["asset_id"]))
            else:
                lcc.log_info("'asset_id' has correct format: asset_object_type")
            check_that_in(
                balance_object,
                "extensions", is_list()
            )

    @staticmethod
    def validate_frozen_balance_object(self, frozen_balance_object):
        if check_that("frozen_balance_object", frozen_balance_object, has_length(6)):
            check_that_in(
                frozen_balance_object,
                "owner", is_(self.echo_acc0),
                "balance", is_dict(),
                "multiplier", is_integer(),
                "extensions", is_list(),
                quiet=True
            )
            balance = frozen_balance_object["balance"]
            if check_that("balance", balance, has_length(2)):
                check_that_in(
                    balance,
                    "amount", is_integer(),
                    quiet=True
                )
            if not self.type_validator.is_asset_id(balance["asset_id"]):
                lcc.log_error("Wrong format of 'asset_id', got: {}".format(balance["asset_id"]))
            else:
                lcc.log_info("'asset_id' has correct format")
            if not self.type_validator.is_frozen_balance_id(frozen_balance_object["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(frozen_balance_object["id"]))
            else:
                lcc.log_info("'id' has correct format: frozen_balance_type")
            if not self.type_validator.is_iso8601(frozen_balance_object["unfreeze_time"]):
                lcc.log_error("Wrong format of 'unfreeze_time', got: {}".format(frozen_balance_object["unfreeze_time"]))
            else:
                lcc.log_info("'unfreeze_time' has correct format: iso8601")

    @staticmethod
    def validate_committee_frozen_balance_object(self, committee_frozen_balance_object):
        if check_that("committee_frozen_balance_object", committee_frozen_balance_object, has_length(4)):
            balance = committee_frozen_balance_object["balance"]
            check_that("committee_frozen_balance_object", balance["amount"], is_integer(), quiet=True)
            if not self.type_validator.is_asset_id(balance["asset_id"]):
                lcc.log_error("Wrong format of 'asset_id', got: {}".format(
                              committee_frozen_balance_object["asset_id"]))
            else:
                lcc.log_info("'asset_id' has correct format")
            if not self.type_validator.is_committee_frozen_balance_id(committee_frozen_balance_object["id"]):
                lcc.log_error("Wrong format of 'committee_frozen_balance_id', got: {}".format(
                              committee_frozen_balance_object["asset_id"]))
            else:
                lcc.log_info("'committee_frozen_balance_id' has correct format")
            if not self.type_validator.is_committee_member_id(committee_frozen_balance_object["owner"]):
                lcc.log_error("Wrong format of 'committee_member_id', got: {}".format(
                              committee_frozen_balance_object["asset_id"]))
            else:
                lcc.log_info("'committee_member_id' has correct format")


# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import has_length, is_integer, check_that_in, check_that, is_dict, is_list,\
    require_that, is_str


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

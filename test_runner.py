# -*- coding: utf-8 -*-
import json
import os
import sys
import time

from project import BLOCK_RELEASE_INTERVAL, RESOURCES_DIR

from echopy import Echo

if "BASE_URL" not in os.environ:
    BASE_URL = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
else:
    BASE_URL = os.environ["BASE_URL"]

categories = [
    # API SECTION
    'api',
    'login_api',
    'asset_api',
    'history_api',
    'network_broadcast_api',
    'registration_api',
    'database_api',
    'connection_to_apis',

    # database_api section
    'database_api_objects',
    'database_api_subscriptions',
    'database_api_blocks_transactions',
    'database_api_globals',
    'database_api_keys',
    'database_api_accounts',
    'database_api_contracts',
    'database_api_balances',
    'database_api_assets',
    'database_api_committee_members',
    'database_api_authority_validation',
    'database_api_proposed_transactions',
    'database_api_sidechain_ethereum',
    'database_api_sidechain_erc20',
    'database_api_sidechain_bitcoin',
    'database_api_contract_fee_pool',

    # OPERATIONS SECTION
    'operations',
    'account_management_operations',
    'assert_conditions_operations',
    'asset_management_operations',
    'balance_object_operations',
    'committee_members_operations',
    'contract_operations',
    'sidechain_operations',
    'custom_extension_operations',
    'assets_market_operations',
    'proposal_operations',
    'asset_transfer_operations',
    'vesting_balances_operations',
    'withdrawal_permissions_operations',
    'sidechain',
    'sidechain_ethereum',
    'sidechain_erc20',
    'sidechain_bitcoin',
    'scenarios',

    # database_api sub tags: accounts, contracts and balances
    'database_api_first_pipeline',

    # rest database_api sub tags
    'database_api_second_pipeline',
]

types = [
    # TEST TYPES
    "main",
    "positive",
    "negative"
]


def process_filters(filters):
    category_filters = []
    type_filters = []
    for pytests_filter in filters:
        filter_negation = not pytests_filter.startswith("^")
        if not filter_negation:
            pytests_filter = pytests_filter[1:]
        if pytests_filter in types:
            type_filters.append([pytests_filter, filter_negation])
        else:
            category_filters.append([pytests_filter, filter_negation])

    command = ""
    if len(category_filters):
        command = "{}-a ".format(command)
        for category_filter in category_filters:
            if category_filter[1]:
                command = "{}{} ".format(command, category_filter[0])
            else:
                command = "{}^{} ".format(command, category_filter[0])

    if len(type_filters):
        command = "{}-m ".format(command)
        for type_filter in type_filters:
            if type_filter[1]:
                command = "{}{}:type ".format(command, type_filter[0])
            else:
                command = "{}^{}:type ".format(command, type_filter[0])

    return command


PYTESTS_FILTERS = "" if "PYTESTS_FILTERS" not in os.environ else os.environ["PYTESTS_FILTERS"].lower().split(":")
PYTESTS_FILTER_COMMAND = process_filters(PYTESTS_FILTERS)


def get_head_block_num(echo_connection):
    return echo_connection.api.database.get_dynamic_global_properties()["head_block_number"]


def run(echo_connection, filter_command):
    if get_head_block_num(echo_connection):
        execution_status = os.system(
            "if ! lcc run {}--exit-error-on-failure; then lcc report --failed; exit 1; fi".format(filter_command)
        )
        sys.exit(1 if execution_status > 1 else execution_status)
    else:
        time.sleep(BLOCK_RELEASE_INTERVAL)
        run(echo_connection, filter_command)


echo = Echo()
echo.connect(BASE_URL)
run(echo, PYTESTS_FILTER_COMMAND)

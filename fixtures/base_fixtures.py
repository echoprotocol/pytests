# -*- coding: utf-8 -*-
import random
import string

import lemoncheesecake.api as lcc

NUM_RANGE_1 = 100
NUM_RANGE_2 = 1000
RANGE_OF_STR = 7
RANGE_OF_STR_FOR_HEX = 20


@lcc.fixture(scope="test")
def get_random_number():
    random_num = random.randrange(NUM_RANGE_1, NUM_RANGE_2)
    lcc.log_info("Generated random number: {}".format(random_num))
    return random_num


@lcc.fixture(scope="test")
def get_random_string():
    random_string = ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(RANGE_OF_STR))
    lcc.log_info("Generated random string: {}".format(random_string))
    return random_string


@lcc.fixture(scope="test")
def get_random_hex_string():
    random_string = ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(RANGE_OF_STR_FOR_HEX))
    random_hex_string = ''.join(hex(ord(x))[2:] for x in random_string)
    lcc.log_info("Generated random hex string: {}".format(random_hex_string))
    return random_hex_string


@lcc.fixture(scope="test")
def get_random_valid_account_name():
    random_string = ''.join(
        random.SystemRandom().choice(string.ascii_lowercase) for _ in range(RANGE_OF_STR))
    lcc.log_info("Generated random account_name: {}".format(random_string))
    return random_string


@lcc.fixture(scope="test")
def get_random_character():
    random_character = ''.join(
        random.SystemRandom().choice(string.punctuation))
    lcc.log_info("Generated random punctuation: {}".format(random_character))
    return random_character

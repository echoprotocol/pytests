import random
import string

import lemoncheesecake.api as lcc

NUM_RANGE_1 = 1
NUM_RANGE_2 = 100
RANGE_OF_STR = 7


@lcc.fixture()
def generate_number_between():
    random_num = random.randrange(NUM_RANGE_1, NUM_RANGE_2)
    lcc.log_info("Random number: {}".format(random_num))
    return random_num


@lcc.fixture()
def generate_random_string():
    random_string = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(RANGE_OF_STR))
    lcc.log_info("Generated random string: {}".format(random_string))
    return random_string

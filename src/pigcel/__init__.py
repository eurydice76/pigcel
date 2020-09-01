
import logging

import numpy as np
np.seterr(all='call')


def np_error_handler(type, flag):

    logging.error("floating point error (%s), with flag %s" % (type, flag))


np.seterrcall(np_error_handler)

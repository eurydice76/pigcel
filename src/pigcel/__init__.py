
"""pigcel 

Pigcel is a PyQt-based application for visualizing and computing statistics on various physiological parameters.
The application works with Excel spreadsheets which gather in several sheets the parameters that should be studied.
"""

import logging
import warnings

import numpy as np

warnings.filterwarnings('ignore')

np.seterr(all='call')


def np_error_handler(type, flag):

    logging.error("floating point error (%s), with flag %s" % (type, flag))


np.seterrcall(np_error_handler)

# -*- coding: utf-8 -*-
"""
Author: Rich Koshak
The Hysteresis module provides an implementation that will tell you whether a
value is below, above, or inbetween a target value plus or minus an offset.

Functions
========
    - hysteresis: Returns a value indicating if the value is above, below, or 
      within the hysteresis gap.

License
========
Copyright (c) 2019 Richard Koshak

This program and accomanying materials are made available under the terms of 
the Eclipse Public License 2.0 which is available at 
http://www.eclipse.org/legal/epl-2.0

"""
from org.eclipse.smarthome.core.library.types import QuantityType, DecimalType, PercentType

@log_traceback
def hysteresis(target, value, low=0, high=0):
    """
    Checks if the value is below, above or between the hysteresis gap defined
    by the target-low <= value <= target+high. The function accepts Python 
    primitives, QuantityTypes, DecimalTypes, or PercentTypes or any combination
    of the four types. When using QuantityTypes, the default units of the Units
    of Measure is used.

    Arguments:
        - target: The target value that defines the setpoint for the comparison.
        - value: The value to determine where it is in the hysteresis.
        - low: Value subtracted from target to define the lower bounds of the 
        hysteresis gap. Defaults to 0.
        - high: Value added to target to define the upper bounds of the 
        hystersis gap. Defaults to 0
    Returns:
        - 1 if value is >= target+high
        - 0 if the value is between target-low and target+high or if low and 
        high are both zero and value == target
        - (-1) if value is <= target-low
    """
    def get_float(value):
        """Helper function to normalize all the argumets to primitive floats."""
        if isinstance(value, (QuantityType, DecimalType, PercentType)):
            value = value.floatValue()
        return value

    target = get_float(target)
    value  = get_float(value)
    low    = get_float(low)
    high   = get_float(high)

    if value == target or target - low < value < target + high: rval = 0
    elif value <= (target - low): rval = (-1)
    else: rval = 1
    
    return rval

# Hysteresis test
from core.log import logging, LOG_PREFIX
log = logging.getLogger("{}.TEST.util".format(LOG_PREFIX)) 
try:
    assert hysteresis(30, 30, 1, 1) == 0
    assert hysteresis(30, 29, 1, 1) == -1
    assert hysteresis(30, 31, 1, 1) == 1
    assert hysteresis(30, 30) == 0
    assert hysteresis(30, 31) == 1
    assert hysteresis(30, 29) == -1
    assert hysteresis(QuantityType(u"30 %"), 
                      QuantityType(u"29 %"), 
                      low=QuantityType(u"1 %")) == -1
    assert hysteresis(QuantityType(u"30 %"), QuantityType(u"29 %"), 1, 1) == -1
    assert hysteresis(QuantityType(u"30 %"), 
                      QuantityType(u"31 %"), 
                      high=QuantityType(u"1 %")) == 1
    assert hysteresis(DecimalType(30), 
                      DecimalType(29), 
                      low=DecimalType(1)) == -1
    assert hysteresis(DecimalType(30), DecimalType(29), 1, 1) == -1
    assert hysteresis(DecimalType(30), 
                      DecimalType(31), 
                      high=DecimalType(1)) == 1
    assert hysteresis(PercentType(30), 
                      PercentType(29), 
                      low=PercentType(1)) == -1
    assert hysteresis(PercentType(30), PercentType(29), 1, 1) == -1
    assert hysteresis(PercentType(30), 
                      PercentType(31), 
                      high=PercentType(1)) == 1
    assert hysteresis(QuantityType(u"30 %"), 
                      DecimalType(29), 
                      PercentType(1), 1) == -1

except AssertionError:
    import traceback
    log.error("Exception: {}".format(traceback.format_exc()))
else:
    log.info("hysteresis tests passed!")
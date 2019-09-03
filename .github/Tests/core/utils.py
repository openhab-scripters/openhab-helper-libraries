# Hysteresis test
from core.util import hysteresis
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
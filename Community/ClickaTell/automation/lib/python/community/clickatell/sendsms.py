from core.log import logging, LOG_PREFIX
from core.clickatell import Clickatell
from configuration import clickatell

def sms(message, subscriber='Default'):
    '''
    Sends an SMS message through ClickaTell gateway.
    Example: sms("Hello")
    Example: sms("Hello", 'Amanda')
    @param param1: SMS Text
    @param param2: Subscriber. A numeric phone number or a phonebook name entry (String)
    '''
    log = logging.getLogger(LOG_PREFIX)
    phoneNumber = clickatell['phonebook'].get(subscriber, None)
    if phoneNumber is None:
        if subscriber.isdigit():
            phoneNumber = subscriber
        else:
            log.error("Subscriber "+subscriber+" wasn't found in the phone book")
            return
    gateway = Clickatell(clickatell['user'], clickatell['password'], clickatell['apiid'], clickatell['sender'])
    message = {'to': phoneNumber, 'text': message}
    log.info("Sending SMS to: " + str(phoneNumber))
    retval, msg = gateway.sendmsg(message)
    if retval == True:
        log.info("SMS Sent: " + msg)
    else:
        log.error("Error while sending SMS: " + str(retval))
    return
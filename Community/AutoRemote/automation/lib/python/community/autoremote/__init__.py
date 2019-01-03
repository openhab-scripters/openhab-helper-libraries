import os
from configuration import autoremote_configuration

def sendMessage(message, ttl=300, sender='openHAB'):
    '''
    Sends an autoremote message
    '''

    # Use GCM Server for delivery
    cmd = 'curl -s -G "https://autoremotejoaomgcd.appspot.com/sendmessage" ' \
        + '--data-urlencode "key='+autoremote_configuration['key']+'" ' \
        + '--data-urlencode "password='+autoremote_configuration['password']+'" ' \
        + '--data-urlencode "message='+message+'" ' \
        + '--data-urlencode "sender='+sender+'" ' \
        + '--data-urlencode "ttl='+str(ttl)+'" ' \
        + ' 1>/dev/null 2>&1 &'

    os.system(cmd)
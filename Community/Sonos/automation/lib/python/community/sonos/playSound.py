from org.eclipse.smarthome.core.library.types import PercentType
from core.actions import Audio
from core.utils import getItemValue
from configuration import sonos, customItemNames, PRIO
from org.eclipse.smarthome.core.library.types import OnOffType

from core.log import logging, LOG_PREFIX
ON = OnOffType.ON

def playsound(fileName, ttsPrio=PRIO['MODERATE'], **keywords):
    '''
    Play a sound mp3 file function. First argument is positional and mandatory.
    Remaining arguments are optionally keyword arguments.
    Example: playsound("Hello.mp3")
    Example: playsound("Hello.mp3", PRIO['HIGH'], room='Kitchen', volume=42)
    @param param1: Sound file name to play (positional argument) (files need to be put in the folder conf/sounds)
    @param param2: Priority as defined by PRIO. Defaults to PRIO['MODERATE']
    @param room: Room to play in. Defaults to "All".
    @return: this is a description of what is returned
    '''
    module_name = 'playsound'
    log = logging.getLogger(LOG_PREFIX+'.'+module_name)
    log.setLevel(logging.DEBUG)

    def getDefaultRoom():
        # Search for the default room to speak in
        for the_key, the_value in sonos['rooms'].iteritems():
            if the_value['defaultttsdevice']:
                return the_key
        return 'All'

    if ((getItemValue(customItemNames['allowTTSSwitch'], ON) != ON) and (ttsPrio <= PRIO['MODERATE'])):
        log.info(unicode(customItemNames['allowTTSSwitch']) + " is OFF and ttsPrio is to low to play sound \'" + fileName + "\' at this moment.")
        return False

    room = getDefaultRoom() if 'room' not in keywords else keywords['room']

    rooms = []
    if room == 'All' or room is None:
        for the_key, the_value in sonos['rooms'].iteritems():
            rooms.append(sonos['rooms'][the_key])
            log.debug('Room found: ' + sonos['rooms'][the_key]['name'])
    else:
        sonosSpeaker = sonos['rooms'].get(room, None)
        if sonosSpeaker is None:
            log.error("Room "+room+" wasn't found in the sonos rooms dictionary")
            return
        rooms.append(sonosSpeaker)
        log.debug('Room found: ' + sonosSpeaker['name'])

    for aRoom in rooms:
        ttsVol = None if 'ttsVol' not in keywords else keywords['ttsVol']
        if not ttsVol or ttsVol >= 70:
            if ttsPrio == PRIO['LOW']:
                ttsVol = 30
            elif ttsPrio == PRIO['MODERATE']:
                ttsVol = 40
            elif ttsPrio == PRIO['HIGH']:
                ttsVol = 60
            elif ttsPrio == PRIO['EMERGENCY']:
                ttsVol = 70
            else:
                ttsVol = aRoom['ttsvolume']

        Audio.playSound(aRoom['audiosink'], fileName)
        log.info("playSound: \'" + fileName + "\'" + ' in room: \'' + aRoom['name'] + '\' at volume: \'' + str(ttsVol) + '\'.')

    return True
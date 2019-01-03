from org.eclipse.smarthome.core.library.types import PercentType
from core.actions import Voice
from core.utils import getItemValue
from configuration import sonos, PRIO
from org.eclipse.smarthome.core.library.types import OnOffType

from core.log import logging, LOG_PREFIX
ON = OnOffType.ON

def tts(ttsSay, ttsPrio=PRIO['MODERATE'], **keywords):
    '''
    Text To Speak function. First argument is positional and mandatory.
    Remaining arguments are optionally keyword arguments.
    Example: tts("Hello")
    Example: tts("Hello", PRIO['HIGH'], ttsRoom='Kitchen', ttsVol=42, ttsLang='en-GB', ttsVoice='Brian')
    @param param1: Text to speak (positional argument)
    @param param2: Priority as defined by PRIO. Defaults to PRIO['MODERATE']
    @param ttsRoom: Room to speak in
    @return: this is a description of what is returned
    '''
    module_name = 'speak'
    log = logging.getLogger(LOG_PREFIX+'.'+module_name)
    log.setLevel(logging.INFO)

    def getDefaultRoom():
        # Search for the default room to speak in
        for the_key, the_value in sonos['rooms'].iteritems():
            if the_value['defaultttsdevice']:
                return the_key
        return 'All'

    if ((getItemValue('Sonos_Allow_TTS_And_Sounds', ON) != ON) and (ttsPrio <= PRIO['MODERATE'])):
        log.info("Item Sonos_Allow_TTS_And_Sounds is OFF and ttsPrio is to low to speak \'" + ttsSay + "\' at this moment.")
        return False

    ttsRoom = getDefaultRoom() if 'ttsRoom' not in keywords else keywords['ttsRoom']

    ttsRooms = []
    if ttsRoom == 'All' or ttsRoom is None:
        for the_key, the_value in sonos['rooms'].iteritems():
            ttsRooms.append(sonos['rooms'][the_key])
            log.debug('TTS room found: ' + sonos['rooms'][the_key]['name'])
    else:
        sonosSpeaker = sonos['rooms'].get(ttsRoom, None)
        if sonosSpeaker is None:
            log.error("Room "+ttsRoom+" wasn't found in the sonos rooms dictionary")
            return
        ttsRooms.append(sonosSpeaker)
        log.debug('TTS room found: ' + sonosSpeaker['name'])

    for room in ttsRooms:
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
                ttsVol = room['ttsvolume']

        ttsLang = room['ttslang'] if 'ttsLang' not in keywords else keywords['ttsLang']
        ttsVoice = room['ttsvoice'] if 'ttsVoice' not in keywords else keywords['ttsVoice']
        ttsEngine = room['ttsengine'] if 'ttsEngine' not in keywords else keywords['ttsEngine']
        #Voice.say(ttsSay, ttsEngine + ':' + ttsVoice, room['audiosink'], PercentType(10)) # Notification sound volume doesn't seem to be supported
        Voice.say(ttsSay, ttsEngine + ':' + ttsVoice, room['audiosink'])
        log.info("TTS: Speaking \'" + ttsSay + "\'" + ' in room: \'' + room['name'] + '\' at volume: \'' + str(ttsVol) + '\'.')

    return True
from core.actions import Voice
from core.utils import getItemValue
from configuration import sonos, PRIO
from core.jsr223 import scope
from core.log import logging, LOG_PREFIX

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
    log = logging.getLogger(LOG_PREFIX + ".community.sonos.speak")

    def getDefaultRoom():
        # Search for the default room to speak in
        for the_key, the_value in sonos['rooms'].iteritems():
            if the_value['defaultttsdevice']:
                return the_key
        return 'All'

    if getItemValue(customItemNames['Sonos_Allow_TTS_And_Sounds'], scope.ON) != scope.ON and ttsPrio <= PRIO['MODERATE']:
        log.info("[{}] is OFF and ttsPrio is too low to speak [{}] at this moment".format(customItemNames['Sonos_Allow_TTS_And_Sounds'], ttsSay))
        return False

    ttsRoom = getDefaultRoom() if 'ttsRoom' not in keywords else keywords['ttsRoom']

    ttsRooms = []
    if ttsRoom == 'All' or ttsRoom is None:
        for the_key, the_value in sonos['rooms'].iteritems():
            ttsRooms.append(sonos['rooms'][the_key])
            log.debug("TTS room found: [{}]".format(sonos['rooms'][the_key]['name']))
    else:
        sonosSpeaker = sonos['rooms'].get(ttsRoom, None)
        if sonosSpeaker is None:
            log.warn("Room [{}] wasn't found in the sonos rooms dictionary".format(ttsRoom))
            return
        ttsRooms.append(sonosSpeaker)
        log.debug("TTS room found: [{}]".format(sonosSpeaker['name']))

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
        #Voice.say(ttsSay, ttsEngine + ':' + ttsVoice, room['audiosink'], scope.PercentType(10)) # Notification sound volume doesn't seem to be supported
        Voice.say(ttsSay, "{}:{}".format(ttsEngine, ttsVoice), room['audiosink'])
        log.info("TTS: Speaking [{}] in room [{}] at volume [{}]".format(ttsSay, room['name'], ttsVol)

    return True

def greeting():
    # To use this, you should set up astro.py as described
    # here https://github.com/OH-Jython-Scripters/Script%20Examples/astro.py
    # It will take care of updating the item 'V_TimeOfDay' for you
    timeOfDay = getItemValue('V_TimeOfDay', TIMEOFDAY['DAY'])
    greeting = {
        0: 'Good night',
        1: 'Good morning',
        2: 'Good day',
        3: 'Good evening'
    }
    if timeOfDay in greeting:
        return greeting[timeOfDay]
    else:
        return 'good day'

'''
PURPOSE:
This script will parse all Alexa voice commands, and if they match the text in the rule, it will send a command to an Item
linked to that Alexa device's TTS Channel. For example, I can ask Alexa "Are the doors locked?", and the device that I asked
will respond with "all doors are locked" or a list of the unlocked doors. Additional phrases can be added.

REQUIRES:
    org.openhab.binding.amazonalexacontrol
    A routine setup in the Alexa app that captures the same text you are capturing (I used a volume adjustment for the action)
    
    Items:
    Group    gAlexa_LastVoiceCommand    "Last Voice Command"
    String    DiningRoom_Dot_LastVoiceCommand    "Dining Room: Last Voice Command [%s]"    (gAlexa_LastVoiceCommand)    {channel="amazonechocontrol:xxxxx:xxxxx:xxxxx:lastVoiceCommand"}
    String    DiningRoom_Dot_TTS    "Dining Room: TTS [%s]"    {channel="amazonechocontrol:xxxxx:xxxxx:xxxxx:textToSpeech"}
    String    FamilyRoom_Dot_LastVoiceCommand    "Famiy Room: Last Voice Command [%s]"    (gAlexa_LastVoiceCommand)    {channel="amazonechocontrol:xxxxx:xxxxx:xxxxx:lastVoiceCommand"}
    String    FamilyRoom_Dot_TTS    "Family Room: TTS [%s]"    (gAlexa_LastVoiceCommand)    {channel="amazonechocontrol:xxxxx:xxxxx:xxxxx:textToSpeech"}

The getLockStates function can be removed or replaced. It uses a group (gSecurity) that contains all of my outer doors. 
'''
from core.triggers import when
from core.rules import rule

def getLockStates():
    return "all doors are locked" if items["gSecurity"] == OnOffType.OFF else "the following doors are not locked, \n{}".format("\n".join(map(lambda unlockedLock: unlockedLock.label, filter(lambda lock: lock.state == OnOffType.OFF, list(ir.getItem("gSecurity").getAllMembers())))))

@rule("Alert: Voice command alert")
@when("Member of gAlexa_LastVoiceCommand received update")
def lastVoiceCommandAlert(event):
    lastVoiceCommandAlert.log.debug("LastVoiceCommand received [{}]".format(event.itemState))
    if event.itemState.toString() == "are the doors locked":
        events.sendCommand(event.itemName.replace("LastVoiceCommand", "TTS"), getLockStates())
    #elif event.itemState.toString() == "are the windows closed":
        # do stuff here
